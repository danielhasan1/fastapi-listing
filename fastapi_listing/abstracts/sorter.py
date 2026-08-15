from abc import ABC, abstractmethod
from typing import Dict

from fastapi_listing.context import QueryContext


class AbsSortingStrategy(ABC):

    @abstractmethod
    def sort(self, *, context: QueryContext = None, value: Dict[str, str],
             extra_context: dict = None) -> QueryContext:
        pass
