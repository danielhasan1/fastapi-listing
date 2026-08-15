from abc import abstractmethod, ABC
from typing import List, Dict

from fastapi_listing.abstracts import DaoAbstract
from fastapi_listing.abstracts import AbsSortingStrategy
from fastapi_listing.context import QueryContext
from fastapi_listing.ctyping import FastapiRequest


class AbstractFilterInterceptor(ABC):

    @abstractmethod
    def apply(self, *, context: QueryContext = None, filter_params: List[Dict[str, str]], dao: DaoAbstract = None,
              request: FastapiRequest = None, extra_context: dict = None) -> QueryContext:
        pass


class AbstractSorterInterceptor(ABC):

    @abstractmethod
    def apply(self, *, context: QueryContext = None, strategy: AbsSortingStrategy = None,
              sorting_params: List[Dict[str, str]] = None, extra_context: dict = None) -> QueryContext:
        pass
