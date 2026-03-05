from typing import List

from fastapi import Request
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from app.constants.audit_action import AuditAction
from app.core.redis import expire_cached_user
from app.exceptions.database_exceptions import DatabaseConstraints
from app.exceptions.user_exceptions import CannotRemoveDefaultAdmin, RoleNotFound, UserNotFound
from app.models.role import Role
from app.models.user import CurrentUser, User
from app.services.audit_service import AuditService

class UserService:

    @staticmethod
    def set_roles(db: Session, request: Request, current_user: CurrentUser, user_id: int, role_names: List[str]):

        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserNotFound(current_user=current_user)

        if user.username == "admin" and "admin" not in role_names:
            raise CannotRemoveDefaultAdmin(current_user=current_user)

        roles = db.query(Role).filter(Role.name.in_(role_names)).all()

        if len(roles) != len(role_names):
            raise RoleNotFound(current_user=current_user)

        try:
            # 直接覆盖旧的角色分配
            user.roles = roles

            # 权限变更 --> token 立即失效
            user.token_version += 1

            # 记录审计日志
            AuditService.record(
                db=db,
                action=AuditAction.ASSIGN_ROLE,
                status="success",
                user_id=current_user.id,
                username=current_user.username,
                resource=f"user:{user_id}",
                ip=request.client.host,
                user_agent=request.headers.get("user-agent"),
                detail={"roles": role_names}
            )

            db.commit()
        except IntegrityError:
            db.rollback()
            raise DatabaseConstraints(current_user=current_user)

        # 使 Redis 缓存失效
        expire_cached_user(user.id)

        return user