from abc import ABC, abstractmethod
from fastapi_listing.ctyping import SqlAlchemyQuery


class FilterAbstract(ABC):

    @abstractmethod
    def filter(self, *, field: str = None, value: str = None, query: SqlAlchemyQuery = None):
        pass
