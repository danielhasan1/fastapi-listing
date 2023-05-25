from abc import abstractmethod, ABC
from typing import List, Dict

from fastapi_listing.abstracts import DaoAbstract
from fastapi_listing.abstracts import TableDataSortingStrategy
from fastapi_listing.typing import SqlAlchemyQuery, FastapiRequest


class FilterMechanicsAbstracts(ABC):

    @abstractmethod
    def apply(self, *, query: SqlAlchemyQuery = None, filter_params: List[Dict[str, str]], dao: DaoAbstract = None,
              request: FastapiRequest = None, extra_context: dict = None) -> SqlAlchemyQuery:
        pass


class SorterMechanicsAbstracts(ABC):

    @abstractmethod
    def apply(self, *, query: SqlAlchemyQuery = None, strategy: TableDataSortingStrategy = None,
              sorting_params: List[Dict[str, str]] = None, extra_context: dict = None) -> SqlAlchemyQuery:
        pass
