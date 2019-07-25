import os

from flask import Flask

from .client import ListTheDocs


__version__ = '1.0.0'


def create_app(override_config: dict=None):

    instance_path = os.environ.get('INSTANCE_PATH', None)

    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    app.config.from_mapping(
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, 'listthedocs.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'listthedocs_alchemy.sqlite'),
        ROOT_API_KEY='ROOT-API-KEY',
        LOGIN_DISABLED=False,

        COPYRIGHT='List The Docs',
        TITLE='Software documentation',
        HEADER="<h2>Software documentation</h2>",
        READONLY=False,
    )

    app.config.from_pyfile('config.py', silent=True)
    if override_config is not None:
        app.config.update(override_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    from .entities import db
    db.init_app(app)
    db.create_all(app=app)

    from . import database
    database.init_app(app)

    from . import commands
    app.cli.add_command(commands.add_listthedocs_project)

    # Setup endpoints
    from .controllers import projects, webui, users
    app.register_blueprint(projects.projects_apis)
    app.register_blueprint(users.users_apis)
    app.register_blueprint(webui.webui)

    return app
