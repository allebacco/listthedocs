import os
import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext

from .entities import Project, Version


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():

    db = get_db()

    db.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            logo TEXT DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS versions (
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            UNIQUE(project_id, name)
        );
    """)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def add_project(name: str, description: str, logo: str) -> Project:

    db = get_db()
    db.execute('INSERT INTO projects(name, description, logo) VALUES(?,?,?)', (name, description, logo))
    db.commit()

    return get_project(name)


def get_projects():

    projects = list()

    db = get_db()
    cursor = db.execute('SELECT rowid, name, description, logo FROM projects ORDER BY rowid ASC')
    for row in cursor.fetchall():
        projects.append(Project(row[0], row[1], row[2], row[3]))

    for project in projects:
        cursor = db.execute('SELECT name, url FROM versions WHERE project_id=?', [project.rowid])
        versions = list()
        for row in cursor.fetchall():
            versions.append(Version(row[0], row[1]))
        project.add_versions(versions)

    return projects


def get_project(name: str) -> Project:

    project = None
    db = get_db()
    cursor = db.execute('SELECT rowid, name, description, logo FROM projects WHERE name = ?', [name])
    row = cursor.fetchone()
    if row is None:
        return None

    project = Project(row[0], row[1], row[2], row[3])
    cursor = db.execute('SELECT name, url FROM versions WHERE project_id=?', [project.rowid])
    versions = list()
    for row in cursor.fetchall():
        versions.append(Version(row[0], row[1]))
    project.add_versions(versions)

    return project


def update_project(project_name: str, description: str=None, logo: str=None):

    db = get_db()
    cursor = db.execute('SELECT rowid FROM projects WHERE name=?', [project_name])
    row = cursor.fetchone()
    if row is None:
        return False

    project_id = row[0]

    if description is not None:
        db.execute(
            'UPDATE projects SET description = ? WHERE rowid = ?',
            [description, project_id]
        )

    if logo is not None:
        db.execute(
            'UPDATE projects SET logo = ? WHERE rowid = ?',
            [logo, project_id]
        )

    db.commit()

    return True


def delete_project(project_name):

    db = get_db()
    cursor = db.execute('SELECT rowid FROM projects WHERE name=?', [project_name])
    row = cursor.fetchone()
    if row is None:
        return True

    project_id = row[0]

    db.execute('DELETE FROM versions WHERE project_id=?', [project_id])
    db.execute('DELETE FROM projects WHERE rowid=?', [project_id])
    db.commit()

    return True


def add_version(project: str, version: Version):

    db = get_db()
    cursor = db.execute('SELECT rowid FROM projects WHERE name=?', [project])
    row = cursor.fetchone()
    if row is None:
        return False

    project_id = row[0]

    db.execute(
        'INSERT OR REPLACE INTO versions(project_id, name, url) VALUES(?,?,?)',
        (project_id, version.name, version.url)
    )
    db.commit()

    return True


def remove_version(project_name: str, version_name: str):

    db = get_db()
    cursor = db.execute('SELECT rowid FROM projects WHERE name=?', [project_name])
    row = cursor.fetchone()
    if row is None:
        return False

    project_id = row[0]

    db.execute(
        'DELETE FROM versions WHERE project_id=? AND name=?', (project_id, version_name)
    )
    db.commit()

    return True


def update_version(project_name: str, version_name: str, new_url: str=None):

    db = get_db()
    cursor = db.execute('SELECT rowid FROM projects WHERE name=?', [project_name])
    row = cursor.fetchone()
    if row is None:
        return False

    project_id = row[0]

    if new_url is not None:
        db.execute(
            'UPDATE versions SET url=? WHERE project_id=? AND name=?',
            (new_url, project_id, version_name)
        )

    db.commit()

    return True
