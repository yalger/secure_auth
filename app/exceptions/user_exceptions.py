class UserNotFound(Exception):
    pass


class RoleNotFound(Exception):
    pass


class PermissionDenied(Exception):
    pass


class CannotRemoveDefaultAdmin(Exception):
    pass