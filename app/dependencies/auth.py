from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.redis import cache_user, get_cached_user
from app.db.session import get_db
from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.exceptions.auth_exceptions import InvalidCredentials, UserInactive, TokenInvalidated
from app.exceptions.user_exceptions import PermissionDenied, UserNotFound
from app.models.user import CurrentUser, User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_version = payload.get("token_version")

        if user_id is None:
            raise InvalidCredentials()
    except JWTError:
        raise InvalidCredentials()

    cached = get_cached_user(user_id)

    if not cached:
        # Redis miss → 查数据库
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserNotFound()

        # 缓存完整用户信息到Redis
        cached = {
            "id": user.id,
            "username": user.username,
            "roles": [r.name for r in user.roles],
            "permissions": list(set((p.name for role in user.roles for p in role.permissions))),
            "is_active": user.is_active,
            "token_version": user.token_version
        }
        cache_user(cached, ttl=ACCESS_TOKEN_EXPIRE_MINUTES*60)

    if not cached["is_active"]:
        raise UserInactive()

    if cached["token_version"] != token_version:
        raise TokenInvalidated()

    return CurrentUser(**cached)

def require_permission(permission_name: str):

    def checker(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):

        if permission_name not in current_user.permissions:
            raise PermissionDenied()

        return current_user

    return checker