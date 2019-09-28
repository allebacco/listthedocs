

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


@webui.route('/<project_code>/latest/')
def latest_root(project_code):
    return latest(project_code, '')


@webui.route('/<project_code>/latest/<path:path>')
def latest(project_code, path):
    project = database.get_project(project_code)

    if project is None:
        abort(404)

    latest_version = project.get_latest_version()
    if latest_version is None:
        abort(404)

    latestindex = latest_version.url
    if path:
        # Remove 'index.html' for doc url
        if latestindex.endswith('index.html'):
            latestindex = latestindex[:-len('/index.html')]
        latestlink = '%s/%s' % (latestindex, path)
    else:
        latestlink = latestindex

    return redirect(latestlink)
