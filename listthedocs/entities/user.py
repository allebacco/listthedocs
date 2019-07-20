from datetime import datetime
from abc import abstractmethod

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
