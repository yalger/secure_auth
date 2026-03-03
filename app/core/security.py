from datetime import datetime, timedelta, timezone
import uuid
from jose import jwt
from passlib.context import CryptContext
from app.core.calc_permission import calculate_user_permission_mask
from app.models.user import User
from app.core.redis import cache_user

SECRET_KEY = "abc123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 1小时

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密码加密
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 密码校验
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 创建 JWT
def create_access_token(user: User, expires_delta: timedelta | None = None):

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user.id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
        "token_version": user.token_version
    }

    # 缓存完整用户信息到Redis
    cache_user({
        "id": user.id,
        "username": user.username,
        "roles": [r.name for r in user.roles],
        "permissions": calculate_user_permission_mask(user),
        "is_active": user.is_active,
        "token_version": user.token_version
    }, ttl=ACCESS_TOKEN_EXPIRE_MINUTES*60)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)