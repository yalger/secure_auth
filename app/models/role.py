from turtle import back

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, relationship
from app.db.base import Base
from app.models.associations import user_roles, role_permissions

class Role(Base):
    __tablename__ = "roles"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, unique=True, nullable=False)   # admin, user
    description = mapped_column(String)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")