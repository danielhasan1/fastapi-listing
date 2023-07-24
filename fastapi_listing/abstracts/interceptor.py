from abc import abstractmethod, ABC
from typing import List, Dict

from fastapi_listing.abstracts import DaoAbstract
from fastapi_listing.abstracts import AbsSortingStrategy
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest


class AbstractFilterInterceptor(ABC):

    @abstractmethod
    def apply(self, *, query: SqlAlchemyQuery = None, filter_params: List[Dict[str, str]], dao: DaoAbstract = None,
              request: FastapiRequest = None, extra_context: dict = None) -> SqlAlchemyQuery:
        pass


class AbstractSorterInterceptor(ABC):

    @abstractmethod
    def apply(self, *, query: SqlAlchemyQuery = None, strategy: AbsSortingStrategy = None,
              sorting_params: List[Dict[str, str]] = None, extra_context: dict = None) -> SqlAlchemyQuery:
        pass
