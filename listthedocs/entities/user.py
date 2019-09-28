from datetime import datetime
from abc import abstractmethod
from enum import Enum, unique

from .entity import Entity, db
from .project import Project
from .utils import generate_api_key


@unique
class Roles(Enum):

    PROJECT_MANAGER = 'PROJECT_MANAGER'
    VERSION_MANAGER = 'VERSION_MANAGER'

    @staticmethod
    def is_valid(name: str) -> bool:
        return name in (e.name for e in Roles)


class User(db.Model, Entity):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'api_keys': [k.to_json() for k in self.api_keys],
            'roles': [r.to_json() for r in self.roles]
        }


class ApiKey(db.Model, Entity):

    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    key = db.Column(db.String(), unique=True, nullable=False, default=generate_api_key)
    is_valid = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('api_keys', uselist=True, cascade='delete,all,delete-orphan'))

    def to_json(self) -> dict:
        return {
            'key': self.key,
            'is_valid': self.is_valid,
            'created_at': self.created_at.isoformat(),
        }


class Role(db.Model, Entity):

    __tablename__ = 'roles'
    __table_args__ = (
        db.UniqueConstraint('name', 'project', name='role_on_project'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(), nullable=False)
    project = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('roles', uselist=True, cascade='delete,all,delete-orphan'))

    def to_json(self) -> dict:
        return {
            'role_name': self.name,
            'project_code': self.project,
            'created_at': self.created_at.isoformat()
        }
