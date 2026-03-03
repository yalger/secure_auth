from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, relationship
from app.db.base import Base
from app.models.associations import role_permissions

class Permission(Base):
    __tablename__ = "permissions"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, unique=True, nullable=False)   # user:create
    description = mapped_column(String)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")