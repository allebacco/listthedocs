import requests
import base64
import attr

from typing import List, Union
from datetime import datetime
from abc import ABC, abstractmethod, abstractstaticmethod
from enum import Enum, unique

from .attr_utils import ListOf, String, Bool, DateTime, EnumString


@attr.s
class Version:
    """The documentation version
    """

    name = String()
    url = String()

    def to_json(self) -> dict:
        return attr.asdict(self)


@attr.s
class Project:
    """The project
    """

    name = String()
    description = String()
    logo = String(default=None)
    versions = ListOf(Version, default=tuple())

    def to_json(self) -> dict:
        return attr.asdict(self)

    def get_version(self, version_name) -> Version:
        """Get a documentation version.

        Args:
            version_name(str): The name of the version to get

        Returns:
            Version: The requested version or None if not present
        """
        if len(self.versions) == 0:
            return None

        if version_name == 'latest':
            return self.versions[-1]

        versions = list(filter(lambda v: v.name == version_name, self.versions))
        if len(versions) > 0:
            return versions[0]

        return None


@attr.s
class ApiKey:

    key = String()
    is_valid = Bool()
    created_at = DateTime()

    def to_json(self) -> dict:
        return attr.asdict(self)


@unique
class Roles(Enum):

    UPDATE_PROJECT = 'UPDATE_PROJECT'
    REMOVE_PROJECT = 'REMOVE_PROJECT'
    ADD_VERSION = 'ADD_VERSION'
    UPDATE_VERSION = 'UPDATE_VERSION'
    REMOVE_VERSION = 'REMOVE_VERSION'

    @staticmethod
    def is_valid(name: str) -> bool:
        return name in (e.name for e in Roles)


@attr.s
class Role:

    role_name = EnumString(Roles)
    project_name = String()
    created_at = DateTime(default=None)

    def to_json(self) -> dict:
        return attr.asdict(self)


@attr.s
class User:

    name = String()
    is_admin = String()
    api_keys = ListOf(ApiKey)
    roles = ListOf(Role)
    created_at = DateTime(default=None)

    def to_json(self) -> dict:
        return attr.asdict(self)



class ListTheDocs:
    """ListTheDocs client"""

    def __init__(self, url: str='http://localhost:5000', api_key: str=None):
        """Constructor.

        Keyword Args:
            url(str): The URL the service. Default 'localhost'
            api_key(str): The API Key
        """
        self._base_url = url
        self._session = requests.Session()
        if api_key is not None:
            self._session.headers['Api-Key'] = api_key

    def add_project(self, project: Project) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects'
        response = self._session.post(endpoint_url, json=project.to_json())
        if response.status_code != 201:
            raise RuntimeError('Error during adding project ' + project.name)

        return Project(**response.json())

    def get_projects(self) -> 'tuple[Project]':
        endpoint_url = self._base_url + '/api/v1/projects'
        response = self._session.get(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during getting projects')

        return tuple(Project(**p) for p in response.json())

    def get_project(self, name) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}'.format(name)
        response = self._session.get(endpoint_url)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise RuntimeError('Error during getting project ' + name)

        return Project(**response.json())

    def update_project(self, project_name: str, *, description: str=None, logo: str=None) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}'.format(project_name)

        json = dict()
        if description is not None:
            json['description'] = description
        if logo is not None:
            json['logo'] = logo

        response = self._session.patch(endpoint_url, json=json)
        if response.status_code != 200:
            raise RuntimeError('Error during updating project')

        return Project(**response.json())

    def delete_project(self, project_name: str):
        endpoint_url = self._base_url + '/api/v1/projects/{}'.format(project_name)
        response = self._session.delete(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during removing project')

    def add_version(self, project_name: str, version: Version) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}/versions'.format(project_name)
        response = self._session.post(endpoint_url, json=version.to_json())
        if response.status_code != 201:
            raise RuntimeError('Error during creating project version')

        return Project(**response.json())

    def delete_version(self, project_name: str, version_name: str) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}/versions/{}'.format(project_name, version_name)
        response = self._session.delete(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during deleting version ' + version_name)

        return Project(**response.json())

    def update_version(self, project_name: str, version_name: str, *, url: str) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}/versions/{}'.format(project_name, version_name)

        json = dict()
        if url is not None:
            json['url'] = url

        response = self._session.patch(endpoint_url, json=json)
        if response.status_code != 200:
            raise RuntimeError('Error during updating ' + version_name)

        return Project(**response.json())

    @staticmethod
    def load_logo_from_file(filename: str) -> str:
        """Load a an image for using as a project logo.

        Args:
            filename(str): The filename of the image

        Returns:
            str: The base64 of the image file to embed into the HTML 'img' tag
        """
        with open(filename, 'rb') as f:
            data = f.read()

        return 'data:image/png;base64,' + base64.b64encode(data).decode('utf8')

    def add_user(self, name, *, is_admin=False) -> User:
        endpoint_url = self._base_url + '/api/v1/users'
        response = self._session.post(endpoint_url, json={'name': name, 'is_admin': is_admin})
        if response.status_code != 201:
            raise RuntimeError('Error during adding user ' + name)

        return User(**response.json())

    def get_user(self, name) -> User:
        endpoint_url = self._base_url + '/api/v1/users/' + name
        response = self._session.get(endpoint_url)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise RuntimeError('Error during getting user ' + name)

        return User(**response.json())

    def get_users(self) -> List[User]:
        endpoint_url = self._base_url + '/api/v1/users'
        response = self._session.get(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during getting users ')

        return [User(**u) for u in response.json()]

    def add_role(self, user: Union[str, User], role: Role):
        if isinstance(user, User):
            user = user.name
        endpoint_url = self._base_url + '/api/v1/users/' + user + '/roles'

        response = self._session.patch(endpoint_url, json=[role.to_json()])
        if response.status_code != 200:
            raise RuntimeError(response.json()['message'])

    def get_roles(self, user: Union[str, User]) -> List[Role]:
        if isinstance(user, User):
            user = user.name
        endpoint_url = self._base_url + '/api/v1/users/' + user + '/roles'

        response = self._session.get(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during get roles of user ' + user)

        return [Role(**r) for r in response.json()]

    def remove_role(self, user: Union[str, User], role: Role):
        if isinstance(user, User):
            user = user.name
        endpoint_url = self._base_url + '/api/v1/users/' + user + '/roles'

        response = self._session.delete(endpoint_url, json=[role.to_json()])
        if response.status_code != 200:
            raise RuntimeError(response.json()['message'])
