import os
import tempfile

import pytest

from listthedocs import create_app
from listthedocs.database import get_db, init_db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    db_fd2, db_path2 = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path2,
        'ROOT_API_KEY': 'secret-key',
    })

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)
    os.close(db_fd2)
    os.unlink(db_path2)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
