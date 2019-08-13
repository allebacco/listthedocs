import os

from datetime import datetime
from flask import Blueprint, current_app, abort, Flask, jsonify, redirect, render_template, request

from ..entities import User, ApiKey, Roles
from .. import database
from .utils import json_response
from ..security import ensure_admin, fail_if_readonly


users_apis = Blueprint('users_apis', __name__)


@users_apis.route('/api/v1/users', methods=['POST'])
@ensure_admin
@fail_if_readonly
def add_user():

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})
    if 'name' not in json_data:
        return json_response(400, json={'message': 'name missing from JSON data'})

    name = json_data['name']
    is_admin = json_data.get('is_admin', False)

    user = User(name=name, is_admin=is_admin)
    user.api_keys.append(ApiKey())
    user = database.add_user(user)

    if user is not None:
        return json_response(201, json=user)

    return json_response(400, json={'message': 'Error during adding user ' + name})


@users_apis.route('/api/v1/users/<name>', methods=['GET'])
@ensure_admin
def get_user_by_name(name):
    user = database.get_user_by_name(name)
    if user is None:
        return json_response(404, json={'message': 'User ' + name + ' does not exists'})
    return json_response(200, json=user)


@users_apis.route('/api/v1/users', methods=['GET'])
@ensure_admin
def get_users():
    users = database.get_users()
    return json_response(200, json=users)


@users_apis.route('/api/v1/users/<name>/roles', methods=['GET'])
@ensure_admin
def get_user_roles(name):
    user = database.get_user_by_name(name)
    if user is None:
        return json_response(404, json={'message': 'User ' + name + ' does not exists'})

    return json_response(200, json=user.roles)


@users_apis.route('/api/v1/users/<user_name>/roles', methods=['PATCH'])
@ensure_admin
@fail_if_readonly
def add_user_roles(user_name):

    user = database.get_user_by_name(user_name)
    if user is None:
        return json_response(404, json={'message': 'User ' + user_name + ' does not exists'})

    json_data = request.get_json()
    print(json_data)
    if json_data is None:
        return json_response(400, json={'message': 'Invalid JSON data'})
    if not isinstance(json_data, (list, tuple)):
        return json_response(400, json={'message': 'Expected a list of JSON roles'})

    for json_role in json_data:
        if 'role_name' not in json_role:
            return json_response(400, json={'message': 'role_name missing from JSON data'})
        if 'project_name' not in json_role:
            return json_response(400, json={'message': 'project_name missing from JSON data'})

        role_name = json_role['role_name']
        project_name = json_role['project_name']
        if not Roles.is_valid(role_name):
            return json_response(400, json={'message': 'Invalid role name'})

        ok = database.add_role_to_user(user.name, role_name, project_name)
        if not ok:
            return json_response(400, json={'message': 'Error during adding role to user'})

    return json_response(200, json={'message': 'Roles added to user'})


@users_apis.route('/api/v1/users/<user_name>/roles', methods=['DELETE'])
@ensure_admin
def remove_user_roles(user_name):
    user = database.get_user_by_name(user_name)
    if user is None:
        return json_response(404, json={'message': 'User ' + user_name + ' does not exists'})

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})
    if not isinstance(json_data, (list, tuple)):
        return json_response(400, json={'message': 'Missing or invalid JSON data'})

    for json_role in json_data:
        if 'role_name' not in json_role:
            return json_response(400, json={'message': 'role_name missing from JSON data'})
        if 'project_name' not in json_role:
            return json_response(400, json={'message': 'project_name missing from JSON data'})

        role_name = json_role['role_name']
        project_name = json_role['project_name']
        if not Roles.is_valid(role_name):
            return json_response(400, json={'message': 'Invalid role name'})

        ok = database.remove_role_from_user(user.name, role_name, project_name)
        if not ok:
            return json_response(400, json={'message': 'Error during adding role to user'})

    return json_response(200, json={'message': 'Roles added to user'})
