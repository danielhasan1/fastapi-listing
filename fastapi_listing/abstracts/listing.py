from sqlalchemy.orm import Query
from abc import ABC, abstractmethod
from typing import Type

from fastapi_listing.abstracts import AbsSortingStrategy, \
    AbsPaginatingStrategy
from fastapi_listing.ctyping import ListingResponseType
from fastapi_listing.interface.listing_meta_info import ListingMetaInfo
from fastapi_listing.interface.client_site_params_adapter import ClientSiteParamAdapter
from fastapi_listing.dao import GenericDao


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
    def _paginate(self, query: Query, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
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
    def default_srt_on(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def default_srt_ord(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def paginate_strategy(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def query_strategy(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def sorting_strategy(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def sort_mecha(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def filter_mecha(self) -> str:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def default_dao(self) -> GenericDao:  # type:ignore # noqa
        ...

    @property
    @abstractmethod
    def feature_params_adapter(self) -> ClientSiteParamAdapter:
        ...

    @abstractmethod
    def get_listing(self):
        ...
