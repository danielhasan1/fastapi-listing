from abc import ABC, abstractmethod
from fastapi_listing.context import QueryContext


class FilterAbstract(ABC):

    @abstractmethod
    def filter(self, *, field: str = None, value: str = None, context: QueryContext = None) -> QueryContext:
        pass
