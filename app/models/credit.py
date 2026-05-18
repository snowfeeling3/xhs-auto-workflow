from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class CreditAccount(Base):
    __tablename__ = "credit_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_key = Column(String(64), unique=True, nullable=False, index=True)
    credits = Column(Integer, default=0, nullable=False)
    total_used = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "session_key": self.session_key,
            "credits": self.credits,
            "total_used": self.total_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
