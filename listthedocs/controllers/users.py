import os

from datetime import datetime
from werkzeug.exceptions import HTTPException
from flask import Blueprint, current_app, abort, Flask, jsonify, redirect, render_template, request

from ..entities import User, ApiKey, Roles
from ..database import database
from .utils import json_response, get_json_body, ensure_json_request_fields
from .security import ensure_admin, fail_if_readonly
from .errors import handle_http_errors, handle_generic_errors
from .exceptions import EntityNotFound, EntityConflict, InvalidJSONBody


users_apis = Blueprint('users_apis', __name__)

users_apis.register_error_handler(HTTPException, handle_http_errors)
users_apis.register_error_handler(Exception, handle_generic_errors)


@users_apis.route('/api/v1/users', methods=['POST'])
@ensure_admin
@fail_if_readonly
def add_user():

    json_data = get_json_body()
    ensure_json_request_fields(json_data, ['name'])

    name = json_data['name']
    is_admin = json_data.get('is_admin', False)

    user = User(name=name, is_admin=is_admin)
    user.api_keys.append(ApiKey())
    try:
        user = database.add_user(user)
    except database.DuplicatedUserName:
        raise EntityConflict('user', name)

    return json_response(201, json=user)


@users_apis.route('/api/v1/users/<user_name>', methods=['GET'])
@ensure_admin
def get_user_by_name(user_name):
    user = database.get_user_by_name(user_name)
    if user is None:
        raise EntityNotFound('user', user_name)

    return json_response(200, json=user)


@users_apis.route('/api/v1/users', methods=['GET'])
@ensure_admin
def get_users():
    users = database.get_users()
    return json_response(200, json=users)


@users_apis.route('/api/v1/users/<user_name>/roles', methods=['GET'])
@ensure_admin
def get_user_roles(user_name):
    user = database.get_user_by_name(user_name)
    if user is None:
        raise EntityNotFound('user', user_name)

    return json_response(200, json=user.roles)


@users_apis.route('/api/v1/users/<user_name>/roles', methods=['PATCH'])
@ensure_admin
@fail_if_readonly
def add_user_roles(user_name):

    user = database.get_user_by_name(user_name)
    if user is None:
        raise EntityNotFound('user', user_name)

    json_data = get_json_body()
    if not isinstance(json_data, (list, tuple)):
        raise InvalidJSONBody()

    for json_role in json_data:
        ensure_json_request_fields(json_role, ('role_name', 'project_name'))

        role_name = json_role['role_name']
        project_name = json_role['project_name']
        if not Roles.is_valid(role_name):
            return json_response(400, json={'message': 'Invalid role name'})

        try:
            database.add_role_to_user(user.name, role_name, project_name)
        except database.UserNotFound:
            raise EntityNotFound('user', user_name)
        except database.ProjectNotFound:
            raise EntityNotFound('project', project_name)

    return json_response(200, json={'message': 'Roles added to user'})


@users_apis.route('/api/v1/users/<user_name>/roles', methods=['DELETE'])
@ensure_admin
def remove_user_roles(user_name):
    user = database.get_user_by_name(user_name)
    if user is None:
        raise EntityNotFound('user', user_name)

    json_data = get_json_body()
    if not isinstance(json_data, (list, tuple)):
        raise InvalidJSONBody()

    for json_role in json_data:
        ensure_json_request_fields(json_role, ('role_name', 'project_name'))

        role_name = json_role['role_name']
        project_name = json_role['project_name']
        if not Roles.is_valid(role_name):
            return json_response(400, json={'message': 'Invalid role name'})

        try:
            database.remove_role_from_user(user.name, role_name, project_name)
        except database.UserNotFound:
            raise EntityNotFound('user', user_name)
        except database.ProjectNotFound:
            raise EntityNotFound('project', project_name)

    return json_response(200, json={'message': 'Roles removed from user'})
