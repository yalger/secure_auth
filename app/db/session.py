from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

# 依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()