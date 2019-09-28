import re

from flask import Response, json as flask_json, request

from ..entities import Entity
from .exceptions import InvalidJSONBody, MissingJSONField, InvalidProjectCode


PROJECT_CODE_REGEX = re.compile(r"^[a-z0-9\-_]+$")


def json_response(code: int, *, json: 'dict or Entity or list[Entity]') -> Response:
    """Create a JSON response:

    Args:
        code(int): The status code

    Keyword Args:
        json(dict,Entity,list[Entity]): The json data. If Entity, it will be converted in a JSON object,
            if list[Entity], it will be converted in a list of JSON objects

    Returns:
        flask.Response: The response
    """

    if isinstance(json, Entity):
        json = json.to_json()
    if isinstance(json, (tuple, list)) and any(isinstance(o, Entity) for o in json):
        json = [o.to_json() for o in json]

    if not isinstance(json, (dict, list, tuple)):
        raise TypeError('json must be a dict, an Entity or a list of entities')

    return Response(response=flask_json.dumps(json), status=code, mimetype='application/json')


def generate_api_key() -> str:
    try:
        # Python >= 3.6
        import secrets
        return secrets.token_urlsafe()
    except ImportError:
        # Python 3.5
        import os
        import base64

        return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('ascii')


def get_json_body():
    body = request.get_json(silent=True)
    if body is None:
        raise InvalidJSONBody()

    return body


def ensure_json_request_fields(json_body: dict, field_names: tuple):
    for field_name in field_names:
        if field_name not in json_body:
            raise MissingJSONField(field_name)


def validate_project_code(code: str):
    if len(code) < 3 or not PROJECT_CODE_REGEX.fullmatch(code):
        raise InvalidProjectCode(code)


def create_project_code(title: str) -> str:
    code = ''
    for c in title:
        if c.isalnum() or c in ('_', '-'):
            code += c
        else:
            code += '-'

    return code.lower()
