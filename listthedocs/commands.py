import click

from flask.cli import with_appcontext

from .database import database
from .entities import Version, Project


@click.command('add_listthedocs')
@with_appcontext
def add_listthedocs_project():

    project = database.get_project('list-the-docs')
    if project is not None:
        print('Project already exists')
        return

    project = Project(
        title='List The Docs', description="Documentation of List The Docs", code='list-the-docs'
    )

    project = database.add_project(project)
    print('Added project', project.title)
    database.add_version(
        project.code, Version('2.0.0', 'https://allebacco.github.io/listthedocs/')
    )
    print('Added version 2.0.0')

