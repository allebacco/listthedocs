import os

from werkzeug.exceptions import HTTPException
from flask import Blueprint, current_app, abort, Flask, jsonify, redirect, render_template, request

from ..entities import Version, Roles
from ..database import database
from .utils import json_response, get_json_body, ensure_json_request_fields
from .security import ensure_admin, fail_if_readonly, ensure_role_on_project
from .errors import handle_http_errors, handle_generic_errors
from .exceptions import InvalidJSONBody, MissingJSONField, InternalError, EntityNotFound, EntityConflict


projects_apis = Blueprint('projects_apis', __name__)

projects_apis.register_error_handler(HTTPException, handle_http_errors)
projects_apis.register_error_handler(Exception, handle_generic_errors)


@projects_apis.route('/api/v1/projects', methods=['POST'])
@fail_if_readonly
@ensure_admin
def add_project():
    json_data = get_json_body()
    ensure_json_request_fields(json_data, ('name', 'description'))

    project_name = json_data['name']
    description = json_data['description']
    logo = json_data.get('logo', None)  # 'http://placehold.it/96x96')

    try:
        project = database.add_project(project_name, description, logo)
    except database.DuplicatedProjectName:
        raise EntityConflict('project', project_name)

    return json_response(201, json=project)


@projects_apis.route('/api/v1/projects', methods=['GET'])
def get_projects():

    projects = database.get_projects()
    return json_response(200, json=projects)


@projects_apis.route('/api/v1/projects/<project_name>', methods=['GET'])
def get_project(project_name):

    project = database.get_project(project_name)
    if project is None:
        raise EntityNotFound('project', project_name)

    return json_response(200, json=project)


@projects_apis.route('/api/v1/projects/<project_name>', methods=['PATCH'])
@fail_if_readonly
@ensure_role_on_project(role=Roles.UPDATE_PROJECT)
def update_project(project_name):

    json_data = get_json_body()

    kwargs = dict()
    if 'logo' in json_data:
        kwargs['logo'] = json_data['logo']
    if 'description' in json_data:
        kwargs['description'] = json_data['description']
    if len(kwargs) == 0:
        return json_response(400, json={'message': 'No field to update'})

    try:
        project = database.update_project(project_name, **kwargs)
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_name)

    return json_response(200, json=project)


@projects_apis.route('/api/v1/projects/<project_name>', methods=['DELETE'])
@fail_if_readonly
@ensure_role_on_project(role=Roles.REMOVE_PROJECT)
def delete_project(project_name):

    database.delete_project(project_name)
    return json_response(200, json={'message': 'Removed project ' + project_name})


@projects_apis.route('/api/v1/projects/<project_name>/versions', methods=['POST'])
@fail_if_readonly
@ensure_role_on_project(role=Roles.ADD_VERSION)
def add_version(project_name):

    json_data = get_json_body()
    ensure_json_request_fields(json_data, ('url', 'name'))

    url = json_data['url']
    version_name = json_data['name']

    try:
        project = database.add_version(project_name, Version(version_name, url))
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_name)
    except database.DuplicatedVersionName:
        raise EntityConflict('version', version_name)

    return json_response(201, json=project)


@projects_apis.route('/api/v1/projects/<project_name>/versions/<version_name>', methods=['DELETE'])
@fail_if_readonly
@ensure_role_on_project(role=Roles.REMOVE_VERSION)
def remove_version(project_name, version_name):

    try:
        database.remove_version(project_name, version_name)
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_name)

    project = database.get_project(project_name)
    return json_response(200, json=project)


@projects_apis.route('/api/v1/projects/<project_name>/versions/<version_name>', methods=['PATCH'])
@fail_if_readonly
@ensure_role_on_project(role=Roles.UPDATE_VERSION)
def update_version(project_name, version_name):

    json_data = get_json_body()
    ensure_json_request_fields(json_data, ['url'])

    url = json_data['url']
    try:
        database.update_version(project_name, version_name, new_url=url)
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_name)

    project = database.get_project(project_name)
    return json_response(200, json=project)
