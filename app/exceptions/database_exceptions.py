from app.exceptions.business_exception import BusinessException
from app.models.user import CurrentUser


class DatabaseConstraints(BusinessException):

    def __init__(self, current_user: CurrentUser | None = None):
        super().__init__("Database constraints violated", 500, current_user=current_user)