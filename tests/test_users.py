import pytest

from datetime import datetime


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def test_get_missing_user(client):

    response = client.get('/api/v2/users/test_user')
    assert response.status_code == 404


def test_add_user_creates_and_returns_the_user_with_apikey(client):

    response = client.post(
        '/api/v2/users',
        json={'name': 'new_user', 'is_admin': True},
    )
    assert response.status_code == 201

    user = response.get_json()
    assert user['name'] == 'new_user'
    assert user['is_admin'] is True
    assert isinstance(user['created_at'], str)
    assert len(user['api_keys']) == 1

    api_key = user['api_keys'][0]
    assert isinstance(api_key['key'], str)
    assert api_key['is_valid'] is True
    assert isinstance(api_key['created_at'], str)


def test_get_user_returns_the_expected_user(client):

    response = client.post(
        '/api/v2/users', json={'name': 'user1', 'is_admin': True}
    )
    assert response.status_code == 201
    response = client.post(
        '/api/v2/users', json={'name': 'user2', 'is_admin': False}
    )
    assert response.status_code == 201

    response = client.get('/api/v2/users/user2')

    user = response.get_json()
    assert user['name'] == 'user2'
    assert user['is_admin'] is False
    assert isinstance(user['created_at'], str)
    assert len(user['api_keys']) == 1

    api_key = user['api_keys'][0]
    assert isinstance(api_key['key'], str)
    assert api_key['is_valid'] is True
    assert isinstance(api_key['created_at'], str)


def test_add_and_remove_user_roles(client):

    response = client.post(
        '/api/v2/users',
        json={'name': 'new_user', 'is_admin': True},
    )
    assert response.status_code == 201

    response = client.post(
        '/api/v2/projects',
        json={'title': 'test_project1', 'description': 'A very long string'},
    )
    assert response.status_code == 201

    response = client.post(
        '/api/v2/projects',
        json={'title': 'test_project2', 'description': 'A very long string'},
    )
    assert response.status_code == 201

    roles_to_add = [
        {
            'role_name': 'PROJECT_MANAGER',
            'project_name': 'test_project1'
        },
    ]
    response = client.patch(
        '/api/v2/users/new_user/roles',
        json=roles_to_add,
    )
    assert response.status_code == 200

    response = client.get('/api/v2/users/new_user/roles')
    assert response.status_code == 200
    roles = response.get_json()
    assert len(roles) == len(roles_to_add)

    response = client.patch(
        '/api/v2/users/new_user/roles',
        json=[{'role_name': 'VERSION_MANAGER', 'project_name': 'test_project2'}],
    )
    assert response.status_code == 200

    response = client.delete(
        '/api/v2/users/new_user/roles',
        json=[{'role_name': 'VERSION_MANAGER', 'project_name': 'test_project2'}],
    )
    assert response.status_code == 200

    response = client.get('/api/v2/users/new_user/roles')
    assert response.status_code == 200

    roles = response.get_json()
    assert len(roles) == len(roles_to_add)
