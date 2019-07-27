from abc import ABC, abstractmethod

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Entity:
    """The base entity class that can convert to a JSON object
    """

    def to_json(self) -> dict:
        raise NotImplementedError()
