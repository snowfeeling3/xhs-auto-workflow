import enum
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_key = Column(String(64), nullable=False, index=True)
    transaction_id = Column(String(100), nullable=False)
    verification_code = Column(String(6), nullable=False)
    amount_yuan = Column(Integer, default=1, nullable=False)
    credits = Column(Integer, default=3, nullable=False)
    status = Column(String(20), default=PaymentStatus.pending.value, nullable=False)
    remark = Column(String(200), default="")
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "session_key": self.session_key,
            "transaction_id": self.transaction_id,
            "verification_code": self.verification_code,
            "amount_yuan": self.amount_yuan,
            "credits": self.credits,
            "status": self.status,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
