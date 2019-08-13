
import natsort

from datetime import datetime

from .entity import Entity, db


class Project(db.Model, Entity):

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    logo = db.Column(db.Text, nullable=True)

    def sort_versions(self):
        self.versions = natsort.natsorted(self.versions, key=Version.sort_by_version)

    def get_version(self, name: str) -> 'Version':
        for v in self.versions:
            if v.name == name:
                return v

        return None

    def get_latest_version(self):
        if len(self.versions) == 0:
            return None

        self.sort_versions()

        return self.versions[-1]

    def to_json(self) -> dict:
        self.sort_versions()
        return {
            "name": self.name,
            "description": self.description,
            "versions": [v.to_json() for v in self.versions],
            'logo': self.logo
        }


class Version(db.Model, Entity):

    __tablename__ = 'versions'
    __table_args__ = (
        db.UniqueConstraint('project_id', 'name', name='project_version_name_unique'),
    )

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    name = db.Column(db.String(), nullable=False)
    url = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    projects = db.relationship(Project, backref=db.backref('versions', uselist=True, cascade='delete,all,delete-orphan'))

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
