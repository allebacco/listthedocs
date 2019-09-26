import pytest

@pytest.fixture
def client(app_without_security):
    """A test client for the app."""
    return app_without_security.test_client()


def test_without_security_add_project_creates_and_returns_the_project(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201


def test_without_security_update_project_description(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.patch('/api/v1/projects/test_project', json={'description': 'Short string'})
    assert response.status_code == 200


def test_without_security_delete_project(client):

    # Add a project
    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.delete('/api/v1/projects/test_project')
    assert response.status_code == 200

    response = client.get('/api/v1/projects/test_project')
    assert response.status_code == 404


def test_without_security_add_version(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.post(
        '/api/v1/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/index.html'}
    )
    assert response.status_code == 201


def test_without_security_remove_version(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.post(
        '/api/v1/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Remove a version
    response = client.delete('/api/v1/projects/test_project/versions/2.0.0')
    assert response.status_code == 200


def test_without_security_update_version_link(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.post(
        '/api/v1/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Patch a version link
    response = client.patch(
        '/api/v1/projects/test_project/versions/2.0.0',
        json={'url': 'www.newexample.com/2.0.0/index.html'}
    )
    assert response.status_code == 200
