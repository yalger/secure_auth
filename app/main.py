from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.seed import init_seed_data
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.exceptions.auth_exceptions import InvalidCredentials, LoginRateLimitExceeded, TokenInvalidated, UserAlreadyExists, UserInactive
from app.exceptions.user_exceptions import CannotRemoveDefaultAdmin, PermissionDenied, RoleNotFound, UserNotFound
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    db = SessionLocal()
    init_seed_data(db)
    db.close()
    yield
    # 关闭时执行（现在可以为空）


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)

@app.exception_handler(UserAlreadyExists)
async def user_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "User already exists"
        }
    )

@app.exception_handler(InvalidCredentials)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "message": "Invalid credentials"
        }
    )

@app.exception_handler(UserInactive)
async def user_inactive_handler(request: Request, exc: UserInactive):
    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "message": "User is inactive"
        }
    )

@app.exception_handler(TokenInvalidated)
async def token_invalidated_handler(request: Request, exc: TokenInvalidated):
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "message": "Token invalidated"
        }
    )

@app.exception_handler(LoginRateLimitExceeded)
async def login_rate_limit_exceeded_handler(request: Request, exc: LoginRateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Login rate limit exceeded"
        }
    )

@app.exception_handler(UserNotFound)
async def user_not_found_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "message": "User not found"
        }
    )

@app.exception_handler(RoleNotFound)
async def role_not_found_handler(request: Request, exc: RoleNotFound):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "Some roles not found"
        }
    )

@app.exception_handler(PermissionDenied)
async def permission_denied_handler(request: Request, exc: PermissionDenied):
    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "message": "Permission denied"
        }
    )

@app.exception_handler(CannotRemoveDefaultAdmin)
async def cannot_remove_default_admin_handler(request: Request, exc: CannotRemoveDefaultAdmin):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "Cannot remove admin role from default admin"
        }
    )

@app.get("/")
def read_root():
    return {"message": "SecureAuth running"}