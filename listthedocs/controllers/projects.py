import os

from werkzeug.exceptions import HTTPException
from flask import Blueprint, current_app, abort, Flask, jsonify, redirect, render_template, request

from ..entities import Version, Roles, Project
from ..database import database
from .utils import json_response, get_json_body, ensure_json_request_fields, \
    validate_project_code, create_project_code
from .security import ensure_admin, fail_if_readonly, ensure_role_on_project
from .errors import handle_http_errors, handle_generic_errors
from .exceptions import InvalidJSONBody, MissingJSONField, InternalError, EntityNotFound, EntityConflict


projects_apis = Blueprint('projects_apis', __name__)

projects_apis.register_error_handler(HTTPException, handle_http_errors)
projects_apis.register_error_handler(Exception, handle_generic_errors)


@projects_apis.route('/api/v2/projects', methods=['POST'])
@fail_if_readonly
@ensure_admin
def add_project():
    json_data = get_json_body()
    ensure_json_request_fields(json_data, ('title', 'description'))

    title = json_data['title']
    code = json_data.get('code', None)
    description = json_data['description']
    logo = json_data.get('logo', None)  # 'http://placehold.it/96x96')

    if code is None:
        code = create_project_code(title)

    validate_project_code(code)

    project = Project(
        code=code, title=title, description=description, logo=logo
    )

    try:
        project = database.add_project(project)
    except database.DuplicatedProjectName:
        raise EntityConflict('project', code)

    return json_response(201, json=project)


@projects_apis.route('/api/v2/projects', methods=['GET'])
def get_projects():

    projects = database.get_projects()
    return json_response(200, json=projects)


@projects_apis.route('/api/v2/projects/<project_code>', methods=['GET'])
def get_project(project_code):

    project = database.get_project(project_code)
    if project is None:
        raise EntityNotFound('project', project_code)

    return json_response(200, json=project)


@projects_apis.route('/api/v2/projects/<project_code>', methods=['PATCH'])
@fail_if_readonly
@ensure_role_on_project(roles=[Roles.PROJECT_MANAGER])
def update_project(project_code):

    json_data = get_json_body()

    kwargs = dict()
    if 'logo' in json_data:
        kwargs['logo'] = json_data['logo']
    if 'description' in json_data:
        kwargs['description'] = json_data['description']
    if 'title' in json_data:
        kwargs['title'] = json_data['title']
    if len(kwargs) == 0:
        return json_response(400, json={'message': 'No field to update'})

    try:
        project = database.update_project(project_code, **kwargs)
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_code)

    return json_response(200, json=project)


@projects_apis.route('/api/v2/projects/<project_code>', methods=['DELETE'])
@fail_if_readonly
@ensure_role_on_project(roles=[Roles.PROJECT_MANAGER])
def delete_project(project_code):

    database.delete_project(project_code)
    return json_response(200, json={'message': 'Removed project ' + project_code})


@projects_apis.route('/api/v2/projects/<project_code>/versions', methods=['POST'])
@fail_if_readonly
@ensure_role_on_project(roles=[Roles.PROJECT_MANAGER, Roles.VERSION_MANAGER])
def add_version(project_code):

    json_data = get_json_body()
    ensure_json_request_fields(json_data, ('url', 'name'))

    url = json_data['url']
    version_name = json_data['name']

    try:
        project = database.add_version(project_code, Version(version_name, url))
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_code)
    except database.DuplicatedVersionName:
        raise EntityConflict('version', version_name)

    return json_response(201, json=project)


@projects_apis.route('/api/v2/projects/<project_code>/versions/<version_name>', methods=['DELETE'])
@fail_if_readonly
@ensure_role_on_project(roles=[Roles.PROJECT_MANAGER, Roles.VERSION_MANAGER])
def remove_version(project_code, version_name):

    try:
        database.remove_version(project_code, version_name)
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_code)

    project = database.get_project(project_code)
    return json_response(200, json=project)


@projects_apis.route('/api/v2/projects/<project_code>/versions/<version_name>', methods=['PATCH'])
@fail_if_readonly
@ensure_role_on_project(roles=[Roles.PROJECT_MANAGER, Roles.VERSION_MANAGER])
def update_version(project_code, version_name):

    json_data = get_json_body()
    ensure_json_request_fields(json_data, ['url'])

    url = json_data['url']
    try:
        database.update_version(project_code, version_name, new_url=url)
    except database.ProjectNotFound:
        raise EntityNotFound('project', project_code)

    project = database.get_project(project_code)
    return json_response(200, json=project)
