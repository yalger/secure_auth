class UserAlreadyExists(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class UserInactive(Exception):
    pass


class TokenInvalidated(Exception):
    pass


class LoginRateLimitExceeded(Exception):
    pass