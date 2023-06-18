from abc import ABC, abstractmethod
from fastapi_listing.ctyping import SqlAlchemyQuery
from typing import Dict


class AbsSortingStrategy(ABC):

    @abstractmethod
    def sort(self, *, query: SqlAlchemyQuery = None, value: Dict[str, str],
             extra_context: dict = None) -> SqlAlchemyQuery:
        pass
