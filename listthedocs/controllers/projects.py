import os

from flask import Blueprint, current_app, abort, Flask, jsonify, redirect, render_template, request

from ..entities import Version
from .. import database
from .utils import json_response


projects_apis = Blueprint('projects_apis', __name__)


@projects_apis.route('/api/v1/projects', methods=['POST'])
def add_project():
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})
    if 'name' not in json_data:
        return json_response(400, json={'message': 'name missing from JSON data'})
    if 'description' not in json_data:
        return json_response(400, json={'message': 'description missing from JSON data'})

    name = json_data['name']
    description = json_data['description']
    logo = json_data.get('logo', None) #'http://placehold.it/96x96')
    project = database.add_project(name, description, logo)

    if project is not None:
        return json_response(201, json=project)

    return json_response(500, json={'message': 'Error during adding project ' + name})


@projects_apis.route('/api/v1/projects', methods=['GET'])
def get_projects():

    projects = database.get_projects()
    return json_response(200, json=projects)


@projects_apis.route('/api/v1/projects/<project_name>', methods=['GET'])
def get_project(project_name):

    project = database.get_project(project_name)
    if project is None:
        return json_response(404, json={'message': 'Project ' + project_name + ' does not exists'})
    return json_response(200, json=project)


@projects_apis.route('/api/v1/projects/<project_name>', methods=['PATCH'])
def update_project(project_name):
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})

    kwargs = dict()
    if 'logo' in json_data:
        kwargs['logo'] = json_data['logo']
    if 'description' in json_data:
        kwargs['description'] = json_data['description']
    if len(kwargs) == 0:
        return json_response(400, json={'message': 'No field to update'})

    ok = database.update_project(project_name, **kwargs)

    if ok:
        project = database.get_project(project_name)
        return json_response(200, json=project)

    return json_response(500, json={'message': 'Error during updating project ' + project_name})


@projects_apis.route('/api/v1/projects/<project_name>', methods=['DELETE'])
def delete_project(project_name):
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    ok = database.delete_project(project_name)
    if ok is True:
        return json_response(200, json={'message': 'Removed project ' + project_name})

    return json_response(500, json={'message': 'Error during removing project ' + project_name})


@projects_apis.route('/api/v1/projects/<project_name>/versions', methods=['POST'])
def add_version(project_name):
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})
    if 'url' not in json_data:
        return json_response(400, json={'message': 'url missing from JSON data'})
    if 'name' not in json_data:
        return json_response(400, json={'message': 'name missing from JSON data'})

    url = json_data['url']
    version_name = json_data['name']
    ok = database.add_version(project_name, Version(version_name, url))
    if not ok:
        return json_response(
            500,
            json={'message': 'Error during adding version {} to project {}'.format(version_name, project_name)}
        )

    project = database.get_project(project_name)
    return json_response(201, json=project)


@projects_apis.route('/api/v1/projects/<project_name>/versions/<version_name>', methods=['DELETE'])
def remove_version(project_name, version_name):
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    database.remove_version(project_name, version_name)

    project = database.get_project(project_name)
    return json_response(200, json=project)


@projects_apis.route('/api/v1/projects/<project_name>/versions/<version_name>', methods=['PATCH'])
def update_version(project_name, version_name):
    if current_app.config['READONLY']:
        return json_response(403, json={'message': 'Service is Readonly'})

    json_data = request.get_json()
    if json_data is None:
        return json_response(400, json={'message': 'Missing or invalid JSON data'})
    if 'url' not in json_data:
        return json_response(400, json={'message': 'url missing from JSON data'})

    url = json_data['url']
    database.update_version(project_name, version_name, new_url=url)

    project = database.get_project(project_name)
    return json_response(200, json=project)
