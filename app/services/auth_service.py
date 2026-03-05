from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.rate_limiter import check_login_rate_limit, clear_login_attempts
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password 
from app.exceptions.auth_exceptions import LoginRateLimitExceeded, UserAlreadyExists, InvalidCredentials, UserInactive
from app.exceptions.user_exceptions import UserNotFound
from app.models.refresh_token import RefreshToken
from app.models.user import User

class AuthService:

    @staticmethod
    def register(db: Session, username: str, email: str, password: str):

        # 1.创建用户
        new_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            is_active=True
        )

        # 2.将新用户插入数据库
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError:  # 用户已存在
            db.rollback()
            raise UserAlreadyExists()

        return new_user

    @staticmethod
    def login(db: Session, ip: str, username: str, password: str):

        if not check_login_rate_limit(ip, username):
            raise LoginRateLimitExceeded()

        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            raise InvalidCredentials()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentials()

        if not user.is_active:
            raise UserInactive()

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user, db=db)

        clear_login_attempts(ip, username)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    def logout(db: Session, refresh_token_str: str):

        refresh = db.query(RefreshToken).filter_by(
            token=refresh_token_str
        ).first()

        if not refresh or refresh.revoked:
            raise InvalidCredentials()
        
        refresh.revoked = True
        db.commit()


    @staticmethod
    def refresh_token(db: Session, refresh_token_str: str):

        refresh = db.query(RefreshToken).filter_by(
            token=refresh_token_str
        ).first()

        if not refresh:
            raise InvalidCredentials()

        if refresh.revoked:
            raise InvalidCredentials()

        if refresh.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise InvalidCredentials()

        user = db.query(User).filter_by(id=refresh.user_id).first()

        if not user:
            raise UserNotFound()

        if not user.is_active:
            raise UserInactive()
        
        access_token = create_access_token(user)

        refresh.revoked = True
        db.commit()

        refresh_token = create_refresh_token(user, db=db)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }