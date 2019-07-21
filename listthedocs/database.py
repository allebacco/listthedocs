import os
import sqlite3
import click

from datetime import datetime
from flask import current_app, g
from flask.cli import with_appcontext

from .entities import Project, Version, User, ApiKey


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
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY ASC,
            name TEXT NOT NULL UNIQUE,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY ASC,
            key TEXT NOT NULL UNIQUE,
            is_valid INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY ASC,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            logo TEXT DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY ASC,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            UNIQUE(project_id, name),
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
    """)


def init_root_user():

    root_user = get_user_by_name('root')
    if root_user is not None:
        return

    key = current_app.config['ROOT_API_KEY']
    user = User('root', True, datetime.utcnow())
    api_key = ApiKey(key, True, user.created_at)
    add_user_with_api_key(user, api_key)


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
        init_root_user()


def add_project(name: str, description: str, logo: str) -> Project:

    db = get_db()
    db.execute('INSERT INTO projects(name, description, logo) VALUES(?,?,?)', (name, description, logo))
    db.commit()

    return get_project(name)


def get_projects():

    projects = list()

    db = get_db()
    cursor = db.execute('SELECT id, name, description, logo FROM projects ORDER BY id ASC')
    for row in cursor.fetchall():
        projects.append(Project(row[0], row[1], row[2], row[3]))

    for project in projects:
        cursor = db.execute('SELECT name, url FROM versions WHERE project_id=?', [project.id])
        versions = list()
        for row in cursor.fetchall():
            versions.append(Version(row[0], row[1]))
        project.add_versions(versions)

    return projects


def get_project(name: str) -> Project:

    project = None
    db = get_db()
    cursor = db.execute('SELECT id, name, description, logo FROM projects WHERE name = ?', [name])
    row = cursor.fetchone()
    if row is None:
        return None

    project = Project(row[0], row[1], row[2], row[3])
    cursor = db.execute('SELECT name, url FROM versions WHERE project_id=?', [project.id])
    versions = list()
    for row in cursor.fetchall():
        versions.append(Version(row[0], row[1]))
    project.add_versions(versions)

    return project


def update_project(project_name: str, description: str=None, logo: str=None):

    db = get_db()
    cursor = db.execute('SELECT id FROM projects WHERE name=?', [project_name])
    row = cursor.fetchone()
    if row is None:
        return False

    project_id = row[0]

    if description is not None:
        db.execute(
            'UPDATE projects SET description = ? WHERE id = ?',
            [description, project_id]
        )

    if logo is not None:
        db.execute(
            'UPDATE projects SET logo = ? WHERE id = ?',
            [logo, project_id]
        )

    db.commit()

    return True


def delete_project(project_name):

    db = get_db()
    cursor = db.execute('SELECT id FROM projects WHERE name=?', [project_name])
    row = cursor.fetchone()
    if row is None:
        return True

    project_id = row[0]

    db.execute('DELETE FROM versions WHERE project_id=?', [project_id])
    db.execute('DELETE FROM projects WHERE id=?', [project_id])
    db.commit()

    return True


def add_version(project: str, version: Version):

    db = get_db()
    cursor = db.execute('SELECT id FROM projects WHERE name=?', [project])
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
    cursor = db.execute('SELECT id FROM projects WHERE name=?', [project_name])
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
    cursor = db.execute('SELECT id FROM projects WHERE name=?', [project_name])
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


def add_user_with_api_key(user: User, api_key: ApiKey) -> User:

    db = get_db()
    cursor = db.execute(
        'INSERT INTO users(name, is_admin, created_at) VALUES(?,?,?)',
        (user.name, user.is_admin, user.created_at.isoformat())
    )
    user_id = cursor.lastrowid
    db.execute(
        'INSERT INTO api_keys(key, is_valid, created_at, user_id) VALUES(?,?,?,?)',
        (api_key.key, api_key.is_valid, api_key.created_at.isoformat(), user_id)
    )
    db.commit()

    return get_user_by_name(user.name)


def get_user_by_name(name: str) -> User:

    db = get_db()
    cursor = db.execute(
        'SELECT id, name, is_admin, created_at FROM users WHERE name = ?', [name]
    )
    row = cursor.fetchone()
    if row is None:
        return None

    created_at = datetime.strptime(row[3], "%Y-%m-%dT%H:%M:%S.%f")
    user = User(row[1], row[2] != 0, created_at, id=row[0])
    user.api_keys = get_api_keys_for_user(name)

    return user


def get_api_keys_for_user(name: str) -> 'list[ApiKey]':

    db = get_db()
    cursor = db.execute('''
        SELECT api_keys.id, api_keys.key, api_keys.is_valid, api_keys.created_at
        FROM api_keys
        LEFT JOIN users ON api_keys.id = users.id
        WHERE users.name = ?
        ''', [name]
    )

    api_keys = list()
    for row in cursor:
        created_at = datetime.strptime(row[3], "%Y-%m-%dT%H:%M:%S.%f")
        api_key = ApiKey(row[1], row[2] != 0, created_at, id=row[0])
        api_keys.append(api_key)

    return api_keys


def get_users() -> User:

    users = list()

    db = get_db()
    cursor = db.execute('SELECT id, name, is_admin, created_at FROM users')
    for row in cursor:
        created_at = datetime.strptime(row[3], "%Y-%m-%dT%H:%M:%S.%f")
        user = User(row[1], row[2] != 0, created_at, id=row[0])
        user.api_keys = get_api_keys_for_user(user.name)
        users.append(user)

    return users


def get_user_for_api_key(api_key: str) -> User:

    db = get_db()
    cursor = db.execute('''
        SELECT users.id, users.name, users.is_admin, users.created_at
        FROM users
        LEFT JOIN api_keys ON api_keys.id = users.id
        WHERE api_keys.key = ? AND api_keys.is_valid = 1
        ''', [api_key]
    )
    row = cursor.fetchone()
    if row is None:
        return None

    created_at = datetime.strptime(row[3], "%Y-%m-%dT%H:%M:%S.%f")
    user = User(row[1], row[2] != 0, created_at, id=row[0])

    return user
