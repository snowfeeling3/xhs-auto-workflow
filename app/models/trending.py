from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from app.database import Base


class TrendingTopic(Base):
    __tablename__ = "trending_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rank = Column(Integer, nullable=False)
    topic_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, default="综合")
    heat_desc = Column(String(50), nullable=False, default="")
    trend_reason = Column(String(500), nullable=False, default="")
    date = Column(Date, nullable=False, default=date.today)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "rank": self.rank,
            "topic_name": self.topic_name,
            "category": self.category,
            "heat_desc": self.heat_desc,
            "trend_reason": self.trend_reason,
            "date": self.date.isoformat() if self.date else None,
        }
