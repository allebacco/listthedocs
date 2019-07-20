import os

from datetime import datetime
from flask import Blueprint, current_app, abort, Flask, jsonify, redirect, render_template, request

from ..entities import User, ApiKey
from .. import database
from .utils import json_response
from ..security import generate_api_key


users_apis = Blueprint('users_apis', __name__)


@users_apis.route('/api/v1/users', methods=['POST'])
def add_user():
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})
    if 'name' not in json_data:
        return json_response(400, json={'message': 'name missing from JSON data'})

    name = json_data['name']
    is_admin = json_data.get('is_admin', False)
    created_at = datetime.utcnow()
    user = User(name, is_admin, created_at)
    api_key = ApiKey(generate_api_key(), True, created_at)
    user = database.add_user_with_api_key(user, api_key)

    if user is not None:
        return json_response(201, json=user)

    return json_response(500, json={'message': 'Error during adding user ' + name})


@users_apis.route('/api/v1/users/<name>', methods=['GET'])
def get_user_by_name(name):
    user = database.get_user_by_name(name)
    if user is None:
        return json_response(404, json={'message': 'User ' + name + ' does not exists'})
    return json_response(200, json=user)
