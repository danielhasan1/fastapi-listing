from abc import ABCMeta, abstractmethod
from typing import Any


class DaoAbstract(metaclass=ABCMeta):

    @property
    @abstractmethod
    def model(self) -> Any:
        """The schema/model this DAO reads and writes. A SQLAlchemy
        declarative class for the default backend, or any plain
        column-name descriptor for a non-ORM backend (e.g. ClickHouseDao)."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def create(self, values) -> Any:
        pass

    @abstractmethod
    def update(self, identifier, values) -> bool:
        pass

    @abstractmethod
    def read(self, identifier, fields) -> Any:
        pass

    @abstractmethod
    def delete(self, identifier) -> bool:
        pass
