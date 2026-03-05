from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.constants.audit_action import AuditAction
from app.core.seed import init_seed_data
from app.db.session import SessionLocal
from app.dependencies.auth import get_current_user
from app.exceptions.business_exception import BusinessException
from app.models.user import CurrentUser
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.services.audit_service import AuditService

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

@app.exception_handler(BusinessException)
async def business_exception_handler(
    request: Request,
    exc: BusinessException
):

    db = SessionLocal()

    try:
        AuditService.record(
            db=db,
            action=AuditAction.API_ERROR,
            status="failed",
            user_id=exc.current_user.id if exc.current_user else None,
            username=exc.current_user.username if exc.current_user else None,
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            detail= {
                "path": request.url.path,
                "error": exc.message
            }
        )
        db.commit()
    finally:
        db.close()

    return JSONResponse(
        status_code=exc.code,
        content={
            "success": False,
            "message": exc.message
        }
    )

@app.get("/")
def read_root():
    return {"message": "SecureAuth running"}