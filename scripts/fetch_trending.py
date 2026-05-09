#!/usr/bin/env python3
"""Fetch trending XiaoHongShu topics via DeepSeek API and store in DB.

Run via cron daily at 8 AM:
  0 8 * * * cd /srv/apps/xhs-auto-workflow && python scripts/fetch_trending.py >> logs/trending.log 2>&1
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.database import SessionLocal, init_db
from app.models.trending import TrendingTopic
from app import config

PROMPT = """你是一个小红书热搜榜单分析助手。请生成今天（{today}）小红书社区中最可能登上热搜的 10 个话题。

要求：
1. 话题覆盖多个领域：美妆护肤、穿搭时尚、美食探店、生活方式、职场成长、情感关系、数码科技、母婴育儿等
2. 每个话题包含：排名(1-10)、话题名称、分类、热度描述（如"150万热度"、"飙升热点"）、上榜理由（1-2句话解释为什么火）
3. 话题要真实、贴近小红书社区生态，不要太假大空
4. 热度描述和上榜理由要具体、有信息量

输出格式（严格 JSON 数组，不要其他任何内容）：
[
  {
    "rank": 1,
    "topic_name": "话题名称",
    "category": "分类",
    "heat_desc": "120万热度",
    "trend_reason": "上榜理由"
  },
  ...
]
"""


def fetch_and_store():
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL,
        temperature=0.7,
        extra_body={"thinking": {"type": "disabled"}},
    )

    today = date.today()
    today_str = today.strftime("%Y年%m月%d日")
    prompt = PROMPT.format(today=today_str)

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Remove markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("\n", 1)[0]

    topics = json.loads(raw)

    init_db()
    db = SessionLocal()
    try:
        db.query(TrendingTopic).filter(TrendingTopic.date == today).delete()
        for t in topics:
            db.add(TrendingTopic(
                rank=t["rank"],
                topic_name=t["topic_name"],
                category=t.get("category", "综合"),
                heat_desc=t.get("heat_desc", ""),
                trend_reason=t.get("trend_reason", ""),
                date=today,
            ))
        db.commit()
        print(f"[OK] Stored {len(topics)} trending topics for {today}")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_store()
