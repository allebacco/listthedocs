import inspect
import functools

from flask import request, current_app, Response, json as flask_json
from werkzeug.local import LocalProxy
from ..database import database
from ..entities import Roles
from .exceptions import ForbiddenAction, UserUnauthorized, ReadonlyLock


def get_authenticated_user():

    api_key = request.headers.get('Api-Key')
    if api_key is None:
        return None

    return database.get_user_for_api_key(api_key)


current_user = LocalProxy(get_authenticated_user)


def ensure_admin(controller_func):

    @functools.wraps(controller_func)
    def decorated_view(*args, **kwargs):
        if current_app.config['LOGIN_DISABLED'] is True:
            return controller_func(*args, **kwargs)

        if current_user._get_current_object() is None:
            raise UserUnauthorized()

        if not current_user.is_admin:
            raise ForbiddenAction()

        return controller_func(*args, **kwargs)

    return decorated_view


def fail_if_readonly(controller_func):

    @functools.wraps(controller_func)
    def decorated_view(*args, **kwargs):
        if current_app.config['READONLY']:
            raise ReadonlyLock()

        return controller_func(*args, **kwargs)

    return decorated_view


def ensure_role_on_project(*, role, allowed_for_admin=True):

    def wrap(controller_func):

        sig = inspect.signature(controller_func)
        if 'project_name' not in sig.parameters:
            raise RuntimeError("'ensure_role_on_project' requires 'project_name' in function signature")

        @functools.wraps(controller_func)
        def decorated_view(project_name, *args, **kwargs):
            if current_app.config['LOGIN_DISABLED'] is True:
                return controller_func(project_name, *args, **kwargs)

            if current_user._get_current_object() is None:
                raise UserUnauthorized()

            if not (current_user.is_admin and allowed_for_admin):
                if not database.check_user_has_role(current_user.name, role.value, project_name):
                    raise ForbiddenAction()

            return controller_func(project_name, *args, **kwargs)

        return decorated_view

    return wrap
