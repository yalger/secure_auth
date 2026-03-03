from app.core.redis import expire_cached_user
from app.exceptions.user_exceptions import CannotRemoveDefaultAdmin, RoleNotFound, UserNotFound
from app.models.user import User
from app.models.role import Role
from sqlalchemy.orm import Session
from typing import List

class UserService:

    @staticmethod
    def set_roles(db: Session, user_id: int, role_names: List[str]):

        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserNotFound()

        if user.username == "admin" and "admin" not in role_names:
            raise CannotRemoveDefaultAdmin()

        roles = db.query(Role).filter(Role.name.in_(role_names)).all()

        if len(roles) != len(role_names):
            raise RoleNotFound()

        # 直接覆盖旧的角色分配
        user.roles = roles

        # 权限变更 --> token 立即失效
        user.token_version += 1
        
        # 使 Redis 缓存失效
        expire_cached_user(user.id)

        db.commit()

        return user