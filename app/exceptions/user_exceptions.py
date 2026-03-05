from app.exceptions.business_exception import BusinessException
from app.models.user import CurrentUser


class UserNotFound(BusinessException):

    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("User not found", 404, current_user)


class RoleNotFound(BusinessException):

    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Some roles not found", 400, current_user)


class PermissionDenied(BusinessException):

    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Permission denied", 403, current_user)


class CannotRemoveDefaultAdmin(BusinessException):

    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Cannot remove default admin", 400, current_user)