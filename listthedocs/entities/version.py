from .entity import Entity


class Version(Entity):

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    @staticmethod
    def sort_by_version(version: 'Version'):
        # See http://natsort.readthedocs.io/en/stable/examples.html
        return version.name.replace('.', '~') + 'z'

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "url": self.url
        }

    def copy(self):
        return Version(self.name, self.url)
