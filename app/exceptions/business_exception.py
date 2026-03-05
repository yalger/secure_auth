from app.models.user import CurrentUser


class BusinessException(Exception):

    def __init__(
        self,
        message: str,
        code: int = 400,
        current_user: CurrentUser | None = None
    ):
        self.message = message
        self.code = code
        self.current_user = current_user