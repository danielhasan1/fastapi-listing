from abc import ABCMeta, abstractmethod
from typing import Union, Dict, List
from fastapi_listing.typing import SqlAlchemyModel


class DaoAbstract(metaclass=ABCMeta):

    @property
    @abstractmethod
    def model(self):
        pass

    @abstractmethod
    def create(self, values: Dict[str, Union[str, int]]) -> SqlAlchemyModel:
        pass

    @abstractmethod
    def update(self, identifier: Dict[str, Union[str, int, list]], values: dict) -> bool:
        pass

    @abstractmethod
    def read(self, identifier: Dict[str, Union[str, int, list]],
             fields: Union[list, str] = "__all__") -> SqlAlchemyModel:
        pass

    @abstractmethod
    def delete(self, ids: List[int]) -> bool:
        pass
