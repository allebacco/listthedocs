from abc import ABC, abstractmethod, abstractstaticmethod
import requests
import base64

class Entity(ABC):

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @abstractstaticmethod
    def from_json(obj: dict) -> 'Entity':
        pass


class Version(Entity):

    def __init__(self, name: str, url: str):
        self._name = name
        self._url = url

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str:
        return self._url

    def to_json(self):
        return {"name": self._name, "url": self._url}

    @staticmethod
    def from_json(obj: dict) -> 'Version':
        return Version(name=obj['name'], url=obj['url'])


class Project(Entity):

    def __init__(self, name: str, description: str, logo: str=None, versions=tuple()):
        self._name = name
        self._description = description
        self._versions = versions
        self._logo = logo

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def logo(self) -> str:
        return self._logo

    @property
    def versions(self) -> str:
        return self._versions

    def get_version(self, version_name) -> Version:
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


class ListTheDocs:

    def __init__(self, host: str='localhost', port: int=5000, protocol: str='http'):
        self._base_url = '{}://{}:{}'.format(protocol, host, port)
        self._session = requests.Session()

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
