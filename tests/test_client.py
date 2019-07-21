
import pytest

from listthedocs import ListTheDocs
from listthedocs.client import Project, Version


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
def ltd_client(client):

    ltd = ListTheDocs()
    ltd._session = MockClientSession(client)
    return ltd


def test_get_missing_project(ltd_client: ListTheDocs):

    project = ltd_client.get_project('test_project')
    assert project is None


def test_get_projects_where_none_exists(ltd_client: ListTheDocs):

    projects = ltd_client.get_projects()
    assert len(projects) == 0


def test_add_project_creates_and_returns_the_project(ltd_client: ListTheDocs):

    project = ltd_client.add_project(Project('test_project', 'A very long string'))

    assert project.name == 'test_project'
    assert project.description == 'A very long string'
    assert project.logo is None


def test_get_project_returns_the_project(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project', 'A very long string'))

    project = ltd_client.get_project('test_project')
    assert project.name == 'test_project'
    assert project.description == 'A very long string'
    assert project.logo is None


def test_get_projects_returns_all_the_projects(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))
    ltd_client.add_project(Project('test_project2', 'description2', logo='img.png'))

    projects = ltd_client.get_projects()
    assert isinstance(projects, tuple)
    assert len(projects) == 2
    assert projects[0].name == 'test_project1'
    assert projects[0].description == 'description1'
    assert projects[0].logo is None
    assert projects[1].name == 'test_project2'
    assert projects[1].description == 'description2'
    assert projects[1].logo == 'img.png'


def test_update_project_description(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))

    project = ltd_client.update_project('test_project1', description='new description')
    assert project.name == 'test_project1'
    assert project.description == 'new description'


def test_update_project_logo(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))

    project = ltd_client.update_project('test_project1', logo='logo.jpg')
    assert project.name == 'test_project1'
    assert project.description == 'description1'
    assert project.logo == 'logo.jpg'


def test_delete_project(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))
    ltd_client.add_version('test_project1', Version('1.0.0', 'www.example.com/index.html'))

    ltd_client.delete_project('test_project1')

    project = ltd_client.get_project('test_project1')
    assert project is None


def test_add_version(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))
    project = ltd_client.add_version('test_project1', Version('1.0.0', 'www.example.com/index.html'))

    assert project.name == 'test_project1'
    assert project.description == 'description1'
    assert project.logo is None
    assert isinstance(project.versions, tuple)
    assert len(project.versions) == 1
    assert project.versions[0].name == '1.0.0'
    assert project.versions[0].url == 'www.example.com/index.html'


def test_remove_version(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))

    # Add multiple versions
    ltd_client.add_version('test_project1', Version('1.0.0', 'www.example.com/1.0.0/index.html'))
    ltd_client.add_version('test_project1', Version('2.0.0', 'www.example.com/2.0.0/index.html'))

    # Remove a version
    ltd_client.delete_version('test_project1', '1.0.0')

    project = ltd_client.get_project('test_project1')
    assert project.name == 'test_project1'
    assert project.description == 'description1'
    assert len(project.versions) == 1
    assert project.versions[0].name == '2.0.0'
    assert project.versions[0].url == 'www.example.com/2.0.0/index.html'


def test_update_version_link(ltd_client: ListTheDocs):

    ltd_client.add_project(Project('test_project1', 'description1'))

    # Add multiple versions
    ltd_client.add_version('test_project1', Version('1.0.0', 'www.example.com/1.0.0/index.html'))
    ltd_client.add_version('test_project1', Version('2.0.0', 'www.example.com/2.0.0/index.html'))

    ltd_client.update_version('test_project1', '2.0.0', url='www.newexample.com/2.0.0/index.html')

    project = ltd_client.get_project('test_project1')
    assert project.name == 'test_project1'
    assert project.description == 'description1'
    assert len(project.versions) == 2
    assert project.versions[0].name == '1.0.0'
    assert project.versions[0].url == 'www.example.com/1.0.0/index.html'
    assert project.versions[1].name == '2.0.0'
    assert project.versions[1].url == 'www.newexample.com/2.0.0/index.html'
