from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # 确保所有模型已导入再建表
    import app.models.post  # noqa
    import app.models.trending  # noqa
    import app.models.credit  # noqa
    import app.models.payment  # noqa
    Base.metadata.create_all(bind=engine)
