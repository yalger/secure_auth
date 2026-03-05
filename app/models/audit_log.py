from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = mapped_column(Integer, primary_key=True, index=True)

    user_id = mapped_column(Integer)
    username = mapped_column(String(50))

    action = mapped_column(String(50), nullable=False)
    resource = mapped_column(String(50))

    ip = mapped_column(String(45))
    user_agent = mapped_column(Text)

    status = mapped_column(String(20), nullable=False)

    detail = mapped_column(JSONB)

    created_at = mapped_column(DateTime, nullable=False, server_default=text("now()"), default=datetime.now)