from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import CurrentUser
from app.schemas.user import UserCreate, UserResponse
from app.schemas.response import APIResponse
from app.schemas.auth import TokenResponse
from app.dependencies.auth import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=APIResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):

    new_user = AuthService.register(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password
    )

    return APIResponse(
        success=True,
        message="User registered successfully",
        data=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    access_token = AuthService.login(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    return TokenResponse(access_token=access_token)

@router.get("/me")
def read_me(
    current_user: CurrentUser = Depends(get_current_user),
):
    return current_user