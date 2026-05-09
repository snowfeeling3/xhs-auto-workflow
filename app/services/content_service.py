import re
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func

from langchain_openai import ChatOpenAI

from app import config
from app.agents.topic_agent import TopicAgent
from app.agents.content_agent import ContentAgent
from app.agents.optimize_agent import OptimizeAgent
from app.agents.risk_agent import RiskAgent
from app.models.post import Post


def _parse_content(text: str) -> dict:
    title_match = re.search(r"标题[：:]\s*(.+?)(?:\n|$)", text)
    title = title_match.group(1).strip() if title_match else ""

    body = text
    tags = ""
    body_lower = text.lower()
    for marker in ["\n标签", "\n标签：", "\ntags：", "\ntags:"]:
        idx = body_lower.find(marker)
        if idx != -1:
            body = text[:idx].strip()
            tags = text[idx + len(marker):].strip().lstrip("：:")
            break

    for marker in ["正文：", "正文:", "\n正文"]:
        idx = body.find(marker)
        if idx != -1:
            body = body[idx + len(marker):].strip()
            break

    return {"title": title, "body": body, "tags": tags}


def _parse_risk(text: str) -> dict:
    level = "low"
    note = ""

    level_match = re.search(r"风险等级[：:]\s*(low|medium|high)", text, re.IGNORECASE)
    if level_match:
        level = level_match.group(1).lower()

    note_match = re.search(r"风险说明[：:]\s*(.+?)(?:\n|$)", text)
    if note_match:
        note = note_match.group(1).strip()

    return {"risk_level": level, "risk_note": note}


def _parse_image_suggestions(text: str) -> list:
    """Extract [插入图片：description] markers."""
    pattern = r'\[插入图片[：:]\s*(.+?)\]'
    return [m.group(1).strip() for m in re.finditer(pattern, text)]


def _format_content_html(text: str) -> str:
    """Convert basic markdown and image markers to HTML."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Image placeholders
    text = re.sub(
        r'\[插入图片[：:]\s*(.+?)\]',
        r'<div class="image-card"><div class="image-card-icon">&#128247;</div><div class="image-card-desc">\1</div></div>',
        text,
    )
    # Paragraphs
    paragraphs = text.split('\n\n')
    text = ''.join(f'<p>{p.replace(chr(10), "<br>")}</p>' if p.strip() else '' for p in paragraphs)
    return text


def _check_daily_limit(db: Session) -> bool:
    today = date.today()
    count = db.query(func.count(Post.id)).filter(
        func.date(Post.created_at) == today
    ).scalar()
    return count < config.FREE_DAILY_LIMIT


class ContentService:
    def __init__(self):
        self._llm = ChatOpenAI(
            model=config.LLM_MODEL,
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            temperature=config.LLM_TEMPERATURE,
            extra_body={"thinking": {"type": "disabled"}},
        )

    def generate(
        self, topic: str, db: Session,
        description: str = "",
        style: str = "",
        length: str = "",
        tone: str = "",
    ) -> dict:
        if not _check_daily_limit(db):
            return {"error": f"今日免费次数已用完（每日 {config.FREE_DAILY_LIMIT} 次），请明天再来"}

        # 构建用户需求上下文字段
        extra_parts = []
        if style:
            extra_parts.append(f"笔记类型：{style}")
        if length:
            extra_parts.append(f"文案长度：{length}")
        if tone:
            extra_parts.append(f"语言风格：{tone}")
        extra_context = "\n".join(extra_parts)

        try:
            topic_prompt = f"请为以下领域生成爆款选题：{topic}"
            if description:
                topic_prompt += f"\n\n用户对内容方向的具体描述（参考此描述来精准定位选题）：\n{description}"
            if extra_context:
                topic_prompt += f"\n\n附加要求：\n{extra_context}"

            topic_agent = TopicAgent(llm=self._llm)
            topic_result = topic_agent.run(topic_prompt)

            content_prompt = f"请根据以下选题信息，创作一篇完整的小红书笔记文案：\n{topic_result}"
            if extra_context:
                content_prompt += f"\n\n请严格遵循以下要求：\n{extra_context}"

            content_agent = ContentAgent(llm=self._llm)
            content_result = content_agent.run(content_prompt)

            optimize_agent = OptimizeAgent(llm=self._llm)
            optimized = optimize_agent.run(
                f"请优化以下小红书文案，提升爆款潜力：\n{content_result}"
            )

            risk_agent = RiskAgent(llm=self._llm)
            risk_result = risk_agent.run(
                f"请检测以下内容的风险等级：\n{optimized}"
            )

            parsed = _parse_content(optimized)
            risk = _parse_risk(risk_result)
            images = _parse_image_suggestions(parsed["body"])
            tags_list = [t.strip() for t in parsed["tags"].split("#") if t.strip()]

            post = Post(
                topic=topic,
                title=parsed["title"],
                content=parsed["body"],
                risk_level=risk["risk_level"],
            )
            db.add(post)
            db.commit()
            db.refresh(post)

            return {
                "id": post.id,
                "title": parsed["title"],
                "content": parsed["body"],
                "tags": parsed["tags"],
                "tags_list": tags_list,
                "image_count": len(images),
                "risk_level": risk["risk_level"],
                "risk_note": risk["risk_note"],
            }

        except Exception as e:
            msg = str(e)
            for sensitive in [config.LLM_API_KEY, "api_key", "Authorization"]:
                if sensitive and sensitive in msg:
                    msg = msg.replace(sensitive, "***")
            return {"error": f"生成失败：{msg}"}
