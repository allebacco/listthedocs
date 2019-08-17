"""Database exceptions
"""

class DatabaseException(Exception):
    pass


class ProjectNotFound(DatabaseException):
    pass


class VersionNotFound(DatabaseException):
    pass


class ApiKeyNotFound(DatabaseException):
    pass


class UserNotFound(DatabaseException):
    pass


class DuplicatedProjectName(DatabaseException):
    pass


class DuplicatedVersionName(DatabaseException):
    pass


class DuplicatedUserName(DatabaseException):
    pass
