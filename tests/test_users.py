import pytest

from datetime import datetime


ADMIN_HEADER = {'Api-Key': 'secret-key'}


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def test_get_missing_user(client):

    response = client.get('/api/v1/users/test_user', headers=ADMIN_HEADER)
    assert response.status_code == 404


def test_add_user_creates_and_returns_the_user_with_apikey(client):

    response = client.post(
        '/api/v1/users',
        json={'name': 'new_user', 'is_admin': True},
        headers=ADMIN_HEADER
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
        '/api/v1/users', json={'name': 'user1', 'is_admin': True}, headers=ADMIN_HEADER
    )
    assert response.status_code == 201
    response = client.post(
        '/api/v1/users', json={'name': 'user2', 'is_admin': False}, headers=ADMIN_HEADER
    )
    assert response.status_code == 201

    response = client.get('/api/v1/users/user2', headers=ADMIN_HEADER)

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
        '/api/v1/users',
        json={'name': 'new_user', 'is_admin': True},
        headers=ADMIN_HEADER
    )
    assert response.status_code == 201

    response = client.post(
        '/api/v1/projects',
        json={'name': 'test_project1', 'description': 'A very long string'},
        headers=ADMIN_HEADER
    )
    assert response.status_code == 201

    response = client.post(
        '/api/v1/projects',
        json={'name': 'test_project2', 'description': 'A very long string'},
        headers=ADMIN_HEADER
    )
    assert response.status_code == 201

    new_roles = [
        {
            'role_name': 'ADD_VERSION',
            'project_name': 'test_project1'
        },
        {
            'role_name': 'REMOVE_PROJECT',
            'project_name': 'test_project1'
        },
        {
            'role_name': 'REMOVE_VERSION',
            'project_name': 'test_project1'
        },
        {
            'role_name': 'UPDATE_VERSION',
            'project_name': 'test_project2'
        },
        {
            'role_name': 'REMOVE_VERSION',
            'project_name': 'test_project2'
        }
    ]
    response = client.patch(
        '/api/v1/users/new_user/roles',
        json=new_roles + [{'role_name': 'ADD_VERSION', 'project_name': 'test_project2'}],
        headers=ADMIN_HEADER
    )
    assert response.status_code == 200

    response = client.delete(
        '/api/v1/users/new_user/roles',
        json=[{'role_name': 'ADD_VERSION', 'project_name': 'test_project2'}],
        headers=ADMIN_HEADER
    )
    assert response.status_code == 200

    response = client.get('/api/v1/users/new_user/roles', headers=ADMIN_HEADER)
    assert response.status_code == 200

    roles = response.get_json()
    assert set(HashableDict(d) for d in roles) == set(HashableDict(d) for d in new_roles)
    assert len(roles) == len(new_roles)
