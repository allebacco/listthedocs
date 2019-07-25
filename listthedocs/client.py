import requests
import base64
import attr

from typing import List, Union
from datetime import datetime
from abc import ABC, abstractmethod, abstractstaticmethod
from enum import Enum, unique

from .attr_utils import ListOf, String, Bool, DateTime, EnumString


class Entity(ABC):
    """Base entity object that can convert to a from JSON.
    """

    @abstractmethod
    def to_json(self) -> dict:
        """Convert self object into JSON represntation.

        Returns:
            dict: The JSON representation
        """
        pass

    @abstractstaticmethod
    def from_json(obj: dict) -> 'Entity':
        """Create an entity instance from the JSON representation.

        Args:
            obj(dict): The JSON representation

        Returns:
            Entity: The entity instance
        """
        pass


class Version(Entity):
    """The documentation version
    """

    def __init__(self, name: str, url: str):
        """Constructor.

        Args:
            name(str): The name of the version (e.g. 1.0.0)
            url(str): The documentation URL
        """
        self._name = name
        self._url = url

    @property
    def name(self) -> str:
        """str: The version Name"""
        return self._name

    @property
    def url(self) -> str:
        """str: The version URL"""
        return self._url

    def to_json(self):
        return {"name": self._name, "url": self._url}

    @staticmethod
    def from_json(obj: dict) -> 'Version':
        return Version(name=obj['name'], url=obj['url'])


class Project(Entity):
    """The project
    """

    def __init__(self, name: str, description: str, logo: str=None, versions=tuple()):
        """Contructor.

        Args:
            name(str): The name of the project
            description(str): The description of the project

        Keyword Args:
            logo(str): The logo of the project
        """
        self._name = name
        self._description = description
        self._versions = versions
        self._logo = logo

    @property
    def name(self) -> str:
        """str: The name of the project"""
        return self._name

    @property
    def description(self) -> str:
        """str: The description of the project"""
        return self._description

    @property
    def logo(self) -> str:
        """The logo of the project"""
        return self._logo

    @property
    def versions(self) -> str:
        """tuple[Version]: The project documentation versions."""
        return self._versions

    def get_version(self, version_name) -> Version:
        """Get a documentation version.

        Args:
            version_name(str): The name of the version to get

        Returns:
            Version: The requested version or None if not present
        """
        if len(self._versions) == 0:
            return None

        if version_name == 'latest':
            return self._versions[-1]

        versions = list(filter(lambda v: v.name == version_name, self._versions))
        if len(versions) > 0:
            return versions[0]

        return None

    def to_json(self):
        return {
            "name": self._name,
            "description": self._description,
            'logo': self._logo,
            "versions": tuple(v.to_json() for v in self._versions),
        }

    @staticmethod
    def from_json(obj: dict) -> 'Project':
        return Project(
            name=obj['name'], description=obj['description'],
            logo=obj.get('logo', None),
            versions=tuple(Version.from_json(v) for v in obj.get('versions', [])),
        )


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

    def to_json(self) -> dict:
        return attr.asdict(self)


@attr.s
class User:

    name = String()
    is_admin = String()
    created_at = DateTime()
    api_keys = ListOf(ApiKey)

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

        return Project.from_json(response.json())

    def get_projects(self) -> 'tuple[Project]':
        endpoint_url = self._base_url + '/api/v1/projects'
        response = self._session.get(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during getting projects')

        return tuple(Project.from_json(p) for p in response.json())

    def get_project(self, name) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}'.format(name)
        response = self._session.get(endpoint_url)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise RuntimeError('Error during getting project ' + name)

        return Project.from_json(response.json())

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

        return Project.from_json(response.json())

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

        return Project.from_json(response.json())

    def delete_version(self, project_name: str, version_name: str) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}/versions/{}'.format(project_name, version_name)
        response = self._session.delete(endpoint_url)
        if response.status_code != 200:
            raise RuntimeError('Error during deleting version ' + version_name)

        return Project.from_json(response.json())

    def update_version(self, project_name: str, version_name: str, *, url: str) -> Project:
        endpoint_url = self._base_url + '/api/v1/projects/{}/versions/{}'.format(project_name, version_name)

        json = dict()
        if url is not None:
            json['url'] = url

        response = self._session.patch(endpoint_url, json=json)
        if response.status_code != 200:
            raise RuntimeError('Error during updating ' + version_name)

        return Project.from_json(response.json())

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

