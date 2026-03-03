from enum import IntFlag


class Permission(IntFlag):
    USER_CREATE = 1 << 0  # 1
    USER_READ   = 1 << 1  # 2
    USER_UPDATE = 1 << 2  # 4
    USER_DELETE = 1 << 3  # 8

