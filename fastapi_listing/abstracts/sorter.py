from abc import ABC, abstractmethod
from fastapi_listing.typing import SqlAlchemyQuery


class TableDataSortingStrategy(ABC):

    @abstractmethod
    def sort(self, *, query: SqlAlchemyQuery = None, value: dict[str, str]) -> SqlAlchemyQuery:
        pass
