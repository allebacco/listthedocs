import pytest


ADMIN_HEADER = {'Api-Key': 'secret-key'}

class UserClient:

    def __init__(self, client, key):
        self._client = client
        self.headers = {'Api-Key': key}

    def get(self, url: str):
        return self._client.get(url, headers=self.headers)

    def post(self, url: str, *, json):
        return self._client.post(url, json=json, headers=self.headers)

    def patch(self, url: str, *, json):
        return self._client.patch(url, json=json, headers=self.headers)

    def delete(self, url: str):
        return self._client.delete(url, headers=self.headers)


class AdminClient:

    def __init__(self, flask_client):
        self._client = flask_client

    def user_client(self, key: str):
        return UserClient(self._client, key)

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


def add_role_on_project(client: AdminClient, user: str, project: str, role: str):
    roles = [{'role_name': role, 'project_code': project}]
    response = client.patch('/api/v2/users/' + user + '/roles', json=roles)
    assert response.status_code == 200


def create_user_client(client: AdminClient, name) -> UserClient:
    response = client.post(
        '/api/v2/users', json={'name': name},
    )
    assert response.status_code == 201
    return client.user_client(response.get_json()['api_keys'][0]['key'])


def test_add_project(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201


def test_update_project_description(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    user_client = create_user_client(client, 'foo')
    add_role_on_project(client, 'foo', 'test_project', 'PROJECT_MANAGER')

    response = user_client.patch('/api/v2/projects/test_project', json={'description': 'Short string'})
    assert response.status_code == 200


def test_delete_project(client):

    # Add a project
    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    user_client = create_user_client(client, 'foo')
    add_role_on_project(client, 'foo', 'test_project', 'PROJECT_MANAGER')

    response = user_client.delete('/api/v2/projects/test_project')
    assert response.status_code == 200

    response = user_client.get('/api/v2/projects/test_project')
    assert response.status_code == 404


@pytest.mark.parametrize('role', ['PROJECT_MANAGER', 'VERSION_MANAGER'])
def test_add_version(client, role):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    user_client = create_user_client(client, 'foo')
    add_role_on_project(client, 'foo', 'test_project', role)

    response = user_client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/index.html'}
    )
    assert response.status_code == 201


@pytest.mark.parametrize('role', ['PROJECT_MANAGER', 'VERSION_MANAGER'])
def test_remove_version(client, role):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    user_client = create_user_client(client, 'foo')
    add_role_on_project(client, 'foo', 'test_project', role)

    response = user_client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Remove a version
    response = user_client.delete('/api/v2/projects/test_project/versions/2.0.0')
    assert response.status_code == 200


@pytest.mark.parametrize('role', ['PROJECT_MANAGER', 'VERSION_MANAGER'])
def test_update_version_link(client, role):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    user_client = create_user_client(client, 'foo')
    add_role_on_project(client, 'foo', 'test_project', role)

    response = user_client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Patch a version link
    response = user_client.patch(
        '/api/v2/projects/test_project/versions/2.0.0',
        json={'url': 'www.newexample.com/2.0.0/index.html'}
    )
    assert response.status_code == 200


def test_add_user(client):

    response = client.post(
        '/api/v2/users',
        json={'name': 'new_user', 'is_admin': True},
    )
    assert response.status_code == 201


def test_get_user(client):

    response = client.get('/api/v2/users/root')
    assert response.status_code == 200
