"""Error management for the REST APIs
"""

from werkzeug.exceptions import HTTPException
from flask import jsonify, Blueprint


def handle_http_errors(exc: HTTPException):
    body = jsonify(
        {
            'code': exc.code,
            'message': exc.description
        }
    )
    return body, exc.code


def handle_generic_errors(exc: Exception):
    body = jsonify(
        {
            'code': 500,
            'message': 'Server Error'
        }
    )
    return body, 500
