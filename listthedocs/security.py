import functools

from flask import request, current_app, Response, json as flask_json
from werkzeug.local import LocalProxy
from . import database
from . entities import Roles


def get_authenticated_user():

    api_key = request.headers.get('Api-Key')
    if api_key is None:
        return None

    return database.get_user_for_api_key(api_key)


current_user = LocalProxy(get_authenticated_user)


def ensure_valid_key(controller_func):

    @functools.wraps(controller_func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get('LOGIN_DISABLED'):
            return controller_func(*args, **kwargs)

        if current_user._get_current_object() is None:
            return Response(
                response=flask_json.dumps({'message': 'Invalid Api-Key'}),
                status=403,
                mimetype='application/json'
            )

        return controller_func(*args, **kwargs)
    return decorated_view


def ensure_admin(controller_func):

    @functools.wraps(controller_func)
    def decorated_view(*args, **kwargs):
        if current_app.config['LOGIN_DISABLED'] is True:
            return controller_func(*args, **kwargs)

        if current_user._get_current_object() is None or current_user.is_admin is False:
            return Response(
                response=flask_json.dumps({'message': 'Invalid Api-Key'}),
                status=403,
                mimetype='application/json'
            )

        return controller_func(*args, **kwargs)

    return decorated_view


def ensure_logged_user(controller_func):

    @functools.wraps(controller_func)
    def decorated_view(*args, **kwargs):
        if current_app.config['LOGIN_DISABLED'] is True:
            return controller_func(*args, **kwargs)

        if current_user._get_current_object() is None:
            return Response(
                response=flask_json.dumps({'message': 'Invalid Api-Key'}),
                status=403,
                mimetype='application/json'
            )

        return controller_func(*args, **kwargs)

    return decorated_view


def fail_if_readonly(controller_func):

    @functools.wraps(controller_func)
    def decorated_view(*args, **kwargs):
        if current_app.config['READONLY']:
            return Response(
                response=flask_json.dumps({'message': 'Service is Readonly'}),
                status=403,
                mimetype='application/json'
            )
        return controller_func(*args, **kwargs)

    return decorated_view


def has_role(role: Roles, project_name: str) -> bool:
    if current_app.config['LOGIN_DISABLED'] is True:
        return True

    return database.check_user_has_role(current_user.name, role.value, project_name)

