

import os

from flask import current_app, abort, redirect, render_template, Blueprint

from ..database import database


webui = Blueprint('webui', __name__, template_folder='templates')


@webui.route('/')
def home():
    projects = database.get_projects()
    return render_template(
        'index.html',
        projects=projects,
        title=current_app.config['TITLE'],
        copyright=current_app.config['COPYRIGHT'],
        header=current_app.config['HEADER'],
    )


@webui.route('/<project_code>/<version_name>/')
def doc_link_root(project_code, version_name):
    return doc_link(project_code, version_name, '')


@webui.route('/<project_code>/<version_name>/<path:path>')
def doc_link(project_code, version_name, path):
    project = database.get_project(project_code)

    if project is None:
        abort(404)

    if version_name == 'latest':
        version = project.get_latest_version()
    else:
        version = project.get_version(version_name)
    if version is None:
        abort(404)

    url = version.url
    if path:
        # Remove 'index.html' for doc url (if present)
        if url.endswith('index.html'):
            url = url[:-len('/index.html')]
        url = '%s/%s' % (url, path)

    return redirect(url)
