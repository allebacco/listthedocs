"""Exceptions for the REST APIs
"""

from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError, NotFound, Conflict, \
    Forbidden, Unauthorized, Locked


class InvalidJSONBody(BadRequest):

    description = 'Expected a JSON body'


class MissingJSONField(BadRequest):

    def __init__(self, field_name: str):
        self.description = "Missing '{}' field".format(field_name)


class InvalidProjectCode(BadRequest):

    def __init__(self, code: str):
        self.description = "Code '{}' is invalid for project.".format(code)
        self.description += " Only a-z, 0-9, '-' and '_' characters are allowed. Minimum 3 characters."


class InternalError(InternalServerError):

    def __init__(self, description: str):
        self.description = description


class EntityNotFound(NotFound):

    def __init__(self, entity_type: str, entity_name: str):
        self.description = "{} '{}' does not exists".format(entity_type.title(), entity_name)


class EntityConflict(Conflict):

    def __init__(self, entity_type: str, entity_name: str, message: str='already exists'):
        self.description = "{} '{}' {}".format(entity_type.title(), entity_name, message)


class ForbiddenAction(Forbidden):

    description = "You don't have the permission to complete this action"


class UserUnauthorized(Unauthorized):

    description = "You have not been authenticated"


class ReadonlyLock(Locked):

    description = "The site is readonly"
