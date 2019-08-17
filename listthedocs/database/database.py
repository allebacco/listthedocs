
from typing import List
from datetime import datetime
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.exc import IntegrityError

from ..entities import Project, Version, User, ApiKey, Role, db
from .exceptions import ApiKeyNotFound, UserNotFound, \
    ProjectNotFound, VersionNotFound, DuplicatedUserName, DuplicatedProjectName, \
    DuplicatedVersionName


def init_root_user():

    root_user = User.query.filter_by(name='root').first()
    if root_user is not None:
        return

    key = current_app.config['ROOT_API_KEY']

    root_user = User(name='root', is_admin=True)
    root_user.api_keys.append(ApiKey(key=key, is_valid=True))
    db.session.add(root_user)
    db.session.commit()


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """

    db.init_app(app)
    db.create_all(app=app)
    with app.app_context():
        init_root_user()


def add_project(name: str, description: str, logo: str) -> Project:

    try:
        project = Project(name=name, description=description, logo=logo)
        db.session.add(project)
        db.session.commit()
    except IntegrityError:
        raise DuplicatedProjectName()

    return project


def get_projects():

    return Project.query.all()


def get_project(name: str) -> Project:

    return Project.query.filter_by(name=name).first()


def update_project(name: str, description: str=None, logo: str=None) -> Project:

    project = get_project(name)
    if project is None:
        raise ProjectNotFound()

    if description is not None:
        project.description = description

    if logo is not None:
        project.logo = logo

    db.session.commit()

    return project


def delete_project(name: str):

    project = get_project(name)
    if project is None:
        return

    db.session.delete(project)
    db.session.commit()


def add_version(project_name: str, version: Version) -> Project:

    project = get_project(project_name)
    if project is None:
        raise ProjectNotFound()

    try:
        project.versions.append(version)
        db.session.commit()
    except IntegrityError:
        raise DuplicatedVersionName()

    return project


def remove_version(project_name: str, version_name: str):

    project = get_project(project_name)
    if project is None:
        raise ProjectNotFound()

    version = project.get_version(version_name)
    if version is None:
        return

    db.session.delete(version)
    db.session.commit()


def update_version(project_name: str, version_name: str, new_url: str=None):

    project = get_project(project_name)
    if project is None:
        raise ProjectNotFound()

    version = project.get_version(version_name)
    if version is None:
        raise VersionNotFound()

    if new_url is not None:
        version.url = new_url

    db.session.commit()


def add_user(user: User) -> User:

    try:
        db.session.add(user)
        db.session.commit()

    except IntegrityError:
        raise DuplicatedUserName()

    return user


def get_user_by_name(name: str) -> User:
    return User.query.filter_by(name=name).first()


def get_users() -> User:

    return User.query.all()


def get_user_for_api_key(api_key: str) -> User:

    key = ApiKey.query.filter_by(key=api_key).first()
    if key is None:
        return None

    return key.user


def add_role_to_user(user_name, role_name, project_name):

    user = get_user_by_name(user_name)
    if user is None:
        raise UserNotFound()

    project = get_project(project_name)
    if project is None:
        raise ProjectNotFound()

    user.roles.append(Role(name=role_name, project=project_name))
    db.session.commit()


def remove_role_from_user(user_name, role_name, project_name):

    user = get_user_by_name(user_name)
    if user is None:
        raise UserNotFound()

    for role in user.roles:
        if role.name == role_name and role.project == project_name:
            user.roles.remove(role)

    db.session.commit()


def check_user_has_role(user_name, role_name, project_name) -> bool:

    user = get_user_by_name(user_name)
    if user is None:
        raise UserNotFound()

    for role in user.roles:
        if role.name == role_name and role.project == project_name:
            return True

    return False
