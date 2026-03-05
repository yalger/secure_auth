from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.db.session import get_db
from app.models.user import CurrentUser
from app.schemas.response import APIResponse
from app.schemas.role import AssignRoleRequest
from app.services.user_service import UserService
from app.dependencies.auth import require_permission

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/{user_id}/roles", response_model=APIResponse)
def set_roles(
    user_id: int,
    request: Request,
    data: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.USER_UPDATE))
):
    user = UserService.set_roles(
        db=db,
        request=request,
        current_user=current_user,
        user_id=user_id,
        role_names=data.role_names
    )

    return APIResponse(
        success=True,
        message="Roles updated successfully",
        data={
            "user_id": user.id,
            "roles": [r.name for r in user.roles]
        }
    )