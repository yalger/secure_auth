from app.exceptions.business_exception import BusinessException
from app.models.user import CurrentUser


class UserAlreadyExists(BusinessException):
    
    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("User already exists", 400, current_user)


class InvalidCredentials(BusinessException):
    
    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Invalid credentials", 401, current_user)


class UserInactive(BusinessException):
    
    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("User is inactive", 403, current_user)


class TokenInvalidated(BusinessException):
    
    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Token has been invalidated", 401, current_user)


class LoginRateLimitExceeded(BusinessException):
    
    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Login rate limit exceeded", 429, current_user)