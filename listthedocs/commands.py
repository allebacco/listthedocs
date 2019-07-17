import click

from flask.cli import with_appcontext

from . import database
from .entities import Version


@click.command('add_listthedocs')
@with_appcontext
def add_listthedocs_project():

    project = database.get_project('ListTheDocs')
    if project is not None:
        print('Project already exists')
        return

    project = database.add_project(
        'ListTheDocs', "Documentation of List The Docs", None
    )
    print('Added project', project.name)
    database.add_version(
        project.name, Version('1.0.0', 'https://allebacco.github.io/listthedocs/')
    )
    print('Added version 1.0.0')

