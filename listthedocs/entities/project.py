
import natsort

from .entity import Entity
from .version import Version


class Project(Entity):

    def __init__(self, rowid: int, name: str, description: str, logo: str):
        self.rowid = rowid
        self.name = name
        self.description = description
        self.versions = list()
        self.logo = logo

    def add_versions(self, versions: 'Iterable[Version]'):
        self.versions = natsort.natsorted(versions, key=Version.sort_by_version)

    def get_latest_version(self):
        if len(self.versions) == 0:
            return None

        return self.versions[-1]

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "versions": [v.to_json() for v in self.versions],
            'logo': self.logo
        }
