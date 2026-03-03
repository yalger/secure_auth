from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.response import APIResponse
from app.schemas.role import AssignRoleRequest
from app.services.user_service import UserService
from app.dependencies.auth import require_permission

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/{user_id}/roles")
def set_roles(
    user_id: int,
    request: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("user:update"))
):
    user = UserService.set_roles(db, user_id, request.role_names)

    return APIResponse(
        success=True,
        message="Roles updated successfully",
        data={
            "user_id": user.id,
            "roles": [r.name for r in user.roles]
        }
    )