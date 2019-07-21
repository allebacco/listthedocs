import secrets

from flask import Response, json as flask_json

from ..entities import Entity


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
    return secrets.token_urlsafe()
