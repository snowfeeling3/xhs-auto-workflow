import re
from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import func

from langchain_openai import ChatOpenAI

import config
from agents.topic_agent import TopicAgent
from agents.content_agent import ContentAgent
from agents.optimize_agent import OptimizeAgent
from agents.risk_agent import RiskAgent
from models.post import Post


def _parse_content(text: str) -> dict:
    """从 Agent 输出中解析标题、正文、标签"""
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
    """从 risk_agent 输出中解析风险等级和说明"""
    level = "low"
    note = ""

    level_match = re.search(r"风险等级[：:]\s*(low|medium|high)", text, re.IGNORECASE)
    if level_match:
        level = level_match.group(1).lower()

    note_match = re.search(r"风险说明[：:]\s*(.+?)(?:\n|$)", text)
    if note_match:
        note = note_match.group(1).strip()

    return {"risk_level": level, "risk_note": note}


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

    def generate(self, topic: str, db: Session) -> dict:
        if not _check_daily_limit(db):
            return {"error": f"今日免费次数已用完（每日 {config.FREE_DAILY_LIMIT} 次），请明天再来"}

        try:
            # 1. 选题
            topic_agent = TopicAgent(llm=self._llm)
            topic_result = topic_agent.run(
                f"请为以下领域生成爆款选题：{topic}"
            )

            # 2. 生成文案
            content_agent = ContentAgent(llm=self._llm)
            content_result = content_agent.run(
                f"请根据以下选题信息，创作一篇完整的小红书笔记文案：\n{topic_result}"
            )

            # 3. 优化
            optimize_agent = OptimizeAgent(llm=self._llm)
            optimized = optimize_agent.run(
                f"请优化以下小红书文案，提升爆款潜力：\n{content_result}"
            )

            # 4. 风险检测
            risk_agent = RiskAgent(llm=self._llm)
            risk_result = risk_agent.run(
                f"请检测以下内容的风险等级：\n{optimized}"
            )

            # 解析结果
            parsed = _parse_content(optimized)
            risk = _parse_risk(risk_result)

            # 存入数据库
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
                "risk_level": risk["risk_level"],
                "risk_note": risk["risk_note"],
            }

        except Exception as e:
            msg = str(e)
            # 从错误消息中移除可能的敏感信息
            for sensitive in [config.LLM_API_KEY, "api_key", "Authorization"]:
                if sensitive and sensitive in msg:
                    msg = msg.replace(sensitive, "***")
            return {"error": f"生成失败：{msg}"}
