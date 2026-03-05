from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import CurrentUser
from app.schemas.auth import LoginRequest, LogoutRequest, TokenResponse
from app.schemas.refresh import RefreshRequest
from app.schemas.response import APIResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=APIResponse)
def register(
    request: Request,
    data: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = AuthService.register(
        db=db,
        request=request,
        username=data.username,
        email=data.email,
        password=data.password
    )

    return APIResponse(
        success=True,
        message="User registered successfully",
        data=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    tokens = AuthService.login(
        db=db,
        request=request,
        username=data.username,
        password=data.password
    )

    return TokenResponse(**tokens)

@router.post("/logout", response_model=APIResponse)
def logout(
    request: Request,
    data: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    AuthService.logout(
        db=db,
        request=request,
        current_user=current_user,
        refresh_token_str=data.refresh_token
    )

    return APIResponse(
        success=True,
        message="Logged out successfully",
        data={
            "user_id": current_user.id,
            "username": current_user.username
        }
    )

@router.get("/me")
def read_me(
    current_user: CurrentUser = Depends(get_current_user)
):
    return current_user

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: Request,
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    tokens = AuthService.refresh_token(
        db=db,
        request=request,
        refresh_token_str=data.refresh_token
    )

    return TokenResponse(**tokens)