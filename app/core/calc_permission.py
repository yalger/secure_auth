from app.core.permissions import Permission
from app.models.user import User
from app.models.role import Role

def calculate_role_permission_mask(role: Role):
    mask = 0
    for permission in role.permissions:
        match permission.name:
            case "user:create":
                mask |= Permission.USER_CREATE
            case "user:read":
                mask |= Permission.USER_READ
            case "user:update":
                mask |= Permission.USER_UPDATE
            case "user:delete":
                mask |= Permission.USER_DELETE
            case _:
                print(f"Invalid permission name: {permission.name}")
    return mask

def calculate_user_permission_mask(user: User):
    mask = 0
    for role in user.roles:
        mask |= calculate_role_permission_mask(role)
    return mask