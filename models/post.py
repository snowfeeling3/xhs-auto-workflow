from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(200), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    risk_level = Column(String(20), nullable=False, default="low")
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "title": self.title,
            "content": self.content,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
