from datetime import datetime
from abc import abstractmethod
from enum import Enum, unique

from .entity import Entity


class ApiKey(Entity):

    def __init__(self, key: str, is_valid: bool, created_at: datetime, id=None):
        self.id = id
        self.key = key
        self.is_valid = is_valid
        self.created_at = created_at

    def to_json(self) -> dict:
        return {
            'key': self.key,
            'is_valid': self.is_valid,
            'created_at': self.created_at.isoformat(),
        }


@unique
class Roles(Enum):

    UPDATE_PROJECT = 'UPDATE_PROJECT'
    REMOVE_PROJECT = 'REMOVE_PROJECT'
    ADD_VERSION = 'ADD_VERSION'
    UPDATE_VERSION = 'UPDATE_VERSION'
    REMOVE_VERSION = 'REMOVE_VERSION'

    @staticmethod
    def is_valid(name: str) -> bool:
        return name in (e.name for e in Roles)


class Role(Entity):

    def __init__(self, name: str, project: str, id: int):
        self.id = id
        self.name = name
        self.project = project

    def to_json(self) -> dict:
        return {'role_name': self.name, 'project_name': self.project}


class User(Entity):

    def __init__(self, name: str, is_admin: bool, created_at: datetime, id: int=None):
        self.id = id
        self.name = name
        self.is_admin = is_admin
        self.created_at = created_at
        self.api_keys = tuple()

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'api_keys': [k.to_json() for k in self.api_keys]
        }
