from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel
from sqlalchemy import String, Integer, Boolean, DateTime, text
from sqlalchemy.orm import mapped_column, relationship
from app.core.permissions import Permission
from app.db.base import Base
from app.models.associations import user_roles

class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(100), unique=True, nullable=False)
    password_hash = mapped_column(String(255), nullable=False)
    is_active = mapped_column(Boolean, nullable=False, server_default=text("true"), default=True)
    created_at = mapped_column(DateTime, nullable=False, server_default=text("now()"), default=datetime.now(timezone.utc))
    token_version = mapped_column(Integer, nullable=False, server_default=text("0"))

    roles = relationship("Role", secondary=user_roles, back_populates="users")

class CurrentUser(BaseModel):
    id: int
    username: str
    roles: List[str]
    permissions: Permission