from abc import ABCMeta, abstractmethod
from typing import Union, Dict, List
from fastapi_listing.ctyping import SqlAlchemyModel


class DaoAbstract(metaclass=ABCMeta):

    @property
    @abstractmethod
    def model(self) -> SqlAlchemyModel:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def create(self, values) -> SqlAlchemyModel:
        pass

    @abstractmethod
    def update(self, identifier, values) -> bool:
        pass

    @abstractmethod
    def read(self, identifier, fields) -> SqlAlchemyModel:
        pass

    @abstractmethod
    def delete(self, identifier) -> bool:
        pass
