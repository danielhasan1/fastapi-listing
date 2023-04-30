from sqlalchemy.orm import Query
from abc import ABC, abstractmethod
from typing import Type

from fastapi_listing.abstracts import TableDataSortingStrategy, \
    TableDataPaginatingStrategy
from fastapi_listing.typing import ListingResponseType
from fastapi_listing.interface.listing_meta_info import ListingMetaInfo


class ListingBase(ABC):

    @abstractmethod
    def _prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    @abstractmethod
    def _apply_sorting(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    @abstractmethod
    def _apply_filters(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    @abstractmethod
    def _paginate(self, query: Query, paginate_strategy: TableDataPaginatingStrategy,
                  extra_context: dict) -> ListingResponseType:
        pass

    @abstractmethod
    def get_response(self, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        pass


class ListingServiceBase(ABC):

    @property
    @abstractmethod
    def filter_mapper(self) -> dict:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def sort_mapper(self) -> dict:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def DEFAULT_SRT_ON(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def DEFAULT_SRT_ORD(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def PAGINATE_STRATEGY(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def QUERY_STRATEGY(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def SORTING_STRATEGY(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def SORT_MECHA(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def FILTER_MECHA(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def dao_kls(self) -> str:  # type:ignore # noqa
        ...

    @abstractmethod
    def get_listing(self):
        ...
