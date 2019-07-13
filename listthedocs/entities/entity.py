from abc import ABC, abstractmethod


class Entity(ABC):
    """The base entity class that can convert to a JSON object
    """

    @abstractmethod
    def to_json(self) -> dict:
        pass
