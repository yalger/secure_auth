from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey, text
from sqlalchemy.orm import mapped_column
from app.db.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token = mapped_column(String, nullable=False, unique=True, index=True)
    expires_at = mapped_column(DateTime, nullable=False)
    revoked = mapped_column(Boolean, nullable=False, server_default=text("false"), default=False)