import pytest


ADMIN_HEADER = {'Api-Key': 'secret-key'}


class AdminClient:

    def __init__(self, flask_client):
        self._client = flask_client

    def get(self, url: str):
        return self._client.get(url, headers=ADMIN_HEADER)

    def post(self, url: str, *, json):
        return self._client.post(url, json=json, headers=ADMIN_HEADER)

    def patch(self, url: str, *, json):
        return self._client.patch(url, json=json, headers=ADMIN_HEADER)

    def delete(self, url: str):
        return self._client.delete(url, headers=ADMIN_HEADER)


@pytest.fixture
def client(app_with_security):
    return AdminClient(app_with_security.test_client())


def add_role_on_project(client, project_name, role):
    roles = [{'role_name': role, 'project_name': project_name}]
    response = client.patch('/api/v1/users/root/roles', json=roles)
    assert response.status_code == 200


def test_add_project(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201


def test_update_project_description(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    add_role_on_project(client, 'test_project', 'UPDATE_PROJECT')

    response = client.patch('/api/v1/projects/test_project', json={'description': 'Short string'})
    assert response.status_code == 200


def test_delete_project(client):

    # Add a project
    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    add_role_on_project(client, 'test_project', 'REMOVE_PROJECT')

    response = client.delete('/api/v1/projects/test_project')
    assert response.status_code == 200

    response = client.get('/api/v1/projects/test_project')
    assert response.status_code == 404


def test_add_version(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    add_role_on_project(client, 'test_project', 'ADD_VERSION')

    response = client.post(
        '/api/v1/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/index.html'}
    )
    assert response.status_code == 201


def test_remove_version(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    add_role_on_project(client, 'test_project', 'ADD_VERSION')
    add_role_on_project(client, 'test_project', 'REMOVE_VERSION')

    response = client.post(
        '/api/v1/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Remove a version
    response = client.delete('/api/v1/projects/test_project/versions/2.0.0')
    assert response.status_code == 200


def test_update_version_link(client):

    response = client.post('/api/v1/projects', json={'name': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    add_role_on_project(client, 'test_project', 'ADD_VERSION')
    add_role_on_project(client, 'test_project', 'UPDATE_VERSION')

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


def test_add_user(client):

    response = client.post(
        '/api/v1/users',
        json={'name': 'new_user', 'is_admin': True},
    )
    assert response.status_code == 201


def test_get_user(client):

    response = client.get('/api/v1/users/root')
    assert response.status_code == 200
