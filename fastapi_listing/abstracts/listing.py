from typing import Type
from abc import ABC, abstractmethod

from sqlalchemy.orm import Query

from fastapi_listing.ctyping import BasePage
from fastapi_listing.abstracts import AbstractListingFeatureParamsAdapter
from fastapi_listing.dao import GenericDao
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
    def _paginate(self, query: Query, listing_meta_info: ListingMetaInfo) -> BasePage:
        pass

    @abstractmethod
    def get_response(self, listing_meta_data) -> BasePage:
        pass


class ListingServiceBase(ABC):

    @property
    @abstractmethod
    def filter_mapper(self) -> dict:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def sort_mapper(self) -> dict:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def default_srt_on(self) -> str:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def default_srt_ord(self) -> str:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def paginate_strategy(self) -> str:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def query_strategy(self) -> str:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def sorting_strategy(self) -> str:  # type:ignore # noqa
        pass

    @sorting_strategy.setter
    def sorting_strategy(self, value):
        pass

    @query_strategy.setter
    def query_strategy(self, value):
        pass

    @paginate_strategy.setter
    def paginate_strategy(self, value):
        pass

    @property
    @abstractmethod
    def sort_mecha(self) -> str:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def filter_mecha(self) -> str:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def default_dao(self) -> GenericDao:  # type:ignore # noqa
        pass

    @property
    @abstractmethod
    def feature_params_adapter(self) -> Type[AbstractListingFeatureParamsAdapter]:
        pass

    @property
    @abstractmethod
    def allow_count_query_by_paginator(self) -> bool:
        pass

    @abstractmethod
    def get_listing(self):
        pass

    @staticmethod
    def _allowed_strategy_types(key: str) -> bool:
        if key not in ("paginate_strategy",
                       "query_strategy",
                       "sorting_strategy",
                       ):
            return False
        return True

    def switch(self, strategy_type: str, strategy_name: str):
        if not self._allowed_strategy_types(strategy_type):
            raise ValueError("unknown strategy type!")
        setattr(self, strategy_type, strategy_name)

    @property
    @abstractmethod
    def max_page_size(self) -> int:
        pass
