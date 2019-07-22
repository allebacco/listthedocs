import pytest

from datetime import datetime

from listthedocs import ListTheDocsAdmin, ListTheDocs
from listthedocs.client import User, ApiKey, Project, Role


ADMIN_HEADER = {'Api-Key': 'secret-key'}


class MockClientResponse:

    def __init__(self, response):
        self._response = response

    @property
    def status_code(self):
        return self._response.status_code

    def json(self):
        return self._response.get_json()


class MockClientSession:

    def __init__(self, flask_client):
        self._client = flask_client

    @staticmethod
    def _fix_url(url):
        return url.replace('http://localhost:5000', '')

    def get(self, url: str):
        url = self._fix_url(url)
        return MockClientResponse(self._client.get(url, headers=ADMIN_HEADER))

    def post(self, url: str, *, json):
        url = self._fix_url(url)
        return MockClientResponse(self._client.post(url, json=json, headers=ADMIN_HEADER))

    def patch(self, url: str, *, json):
        url = self._fix_url(url)
        return MockClientResponse(self._client.patch(url, json=json, headers=ADMIN_HEADER))

    def delete(self, url: str):
        url = self._fix_url(url)
        return MockClientResponse(self._client.delete(url, headers=ADMIN_HEADER))


@pytest.fixture
def admin_client(client):

    ltd = ListTheDocsAdmin()
    ltd._session = MockClientSession(client)
    return ltd


@pytest.fixture
def ltd_client(client):

    ltd = ListTheDocs()
    ltd._session = MockClientSession(client)
    return ltd


def test_add_user_creates_a_new_user(admin_client: ListTheDocsAdmin):

    user = admin_client.add_user('foo', is_admin=True)
    assert isinstance(user, User)
    assert user.name == 'foo'
    assert user.is_admin is True
    assert isinstance(user.api_keys, list)
    assert len(user.api_keys) == 1
    assert isinstance(user.api_keys[0].key, str)
    assert isinstance(user.api_keys[0].created_at, datetime)
    assert user.api_keys[0].is_valid is True


def test_get_user_returns_the_user(admin_client: ListTheDocsAdmin):

    admin_client.add_user('foo')

    user = admin_client.get_user('foo')
    assert isinstance(user, User)
    assert user.name == 'foo'
    assert user.is_admin is False
    assert isinstance(user.api_keys, list)
    assert len(user.api_keys) == 1
    assert isinstance(user.api_keys[0].key, str)
    assert isinstance(user.api_keys[0].created_at, datetime)
    assert user.api_keys[0].is_valid is True


def test_get_users_returns_the_users(admin_client: ListTheDocsAdmin):

    admin_client.add_user('foo')
    admin_client.add_user('bar')

    users = admin_client.get_users()
    assert isinstance(users, list)
    assert len(users) == 3
    users = sorted(users, key=lambda u: u.name)
    assert users[0].name == 'bar'
    assert users[1].name == 'foo'
    assert users[2].name == 'root'


def test_add_role_to_user(ltd_client: ListTheDocs, admin_client: ListTheDocsAdmin):

    ltd_client.add_project(Project('test_project', 'empty description'))

    admin_client.add_role('root', Role(role_name='UPDATE_PROJECT', project_name='test_project'))
