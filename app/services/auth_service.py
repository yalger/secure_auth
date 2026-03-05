from datetime import datetime

from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.constants.audit_action import AuditAction
from app.core.rate_limiter import check_login_rate_limit, clear_login_attempts
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password 
from app.exceptions.auth_exceptions import LoginRateLimitExceeded, UserAlreadyExists, InvalidCredentials, UserInactive
from app.exceptions.database_exceptions import DatabaseConstraints
from app.exceptions.user_exceptions import UserNotFound
from app.models.refresh_token import RefreshToken
from app.models.user import CurrentUser, User
from app.services.audit_service import AuditService

class AuthService:

    @staticmethod
    def register(db: Session, request: Request, username: str, email: str, password: str):

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

            AuditService.record(
                db=db,
                action=AuditAction.REGISTER,
                status="success",
                user_id=new_user.id,
                username=new_user.username,
                ip=request.client.host,
                user_agent=request.headers.get("user-agent")
            )

            db.commit()
        except IntegrityError:  # 用户已存在
            db.rollback()
            raise UserAlreadyExists()

        db.refresh(new_user)
        return new_user

    @staticmethod
    def login(db: Session, request: Request, username: str, password: str):

        ip = request.client.host
        user_agent = request.headers.get("user-agent")

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

        try:
            refresh_token = create_refresh_token(user, db=db)

            AuditService.record(
                db=db,
                action=AuditAction.LOGIN,
                status="success",
                user_id=user.id,
                username=username,
                ip=ip,
                user_agent=user_agent
            )

            db.commit()
        except IntegrityError:
            db.rollback()
            raise DatabaseConstraints()

        access_token = create_access_token(user)
        clear_login_attempts(ip, username)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    def logout(db: Session, request: Request, current_user: CurrentUser, refresh_token_str: str):

        refresh = db.query(RefreshToken).filter_by(
            token=refresh_token_str
        ).first()

        if not refresh or refresh.revoked:
            raise InvalidCredentials(current_user=current_user)

        try:
            refresh.revoked = True

            AuditService.record(
                db=db,
                action=AuditAction.LOGOUT,
                status="success",
                user_id=current_user.id,
                username=current_user.username,
                ip=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            db.commit()
        except IntegrityError:
            db.rollback()
            raise DatabaseConstraints(current_user=current_user)


    @staticmethod
    def refresh_token(db: Session, request: Request, refresh_token_str: str):

        refresh = db.query(RefreshToken).filter_by(
            token=refresh_token_str
        ).first()

        if not refresh:
            raise InvalidCredentials()

        if refresh.revoked:
            raise InvalidCredentials()

        if refresh.expires_at < datetime.now():
            raise InvalidCredentials()

        user = db.query(User).filter_by(id=refresh.user_id).first()

        if not user:
            raise UserNotFound()

        if not user.is_active:
            raise UserInactive()

        try:
            refresh.revoked = True

            refresh_token = create_refresh_token(user, db=db)

            AuditService.record(
                db=db,
                action=AuditAction.REFRESH_TOKEN,
                status="success",
                user_id=user.id,
                username=user.username,
                ip=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            db.commit()
        except IntegrityError:
            db.rollback()
            raise DatabaseConstraints()

        access_token = create_access_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }