import os
import tempfile

import pytest

from listthedocs import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'DATABASE_URI': 'sqlite:///' + db_path,
        'LOGIN_DISABLED': True,
    })

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def app_with_security():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'DATABASE_URI': 'sqlite:///' + db_path,
        'LOGIN_DISABLED': False,
        'ROOT_API_KEY': 'secret-key',
    })

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

