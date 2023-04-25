from sqlalchemy.orm import Query
from abc import ABC
from typing import Type

from fastapi_listing.abstracts import TableDataSortingStrategy, \
    TableDataPaginatingStrategy
from fastapi_listing.typing import ListingResponseType
from fastapi_listing.interface.listing_meta_info import ListingMetaInfo


class ListingBase(ABC):

    def prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    def apply_sorting(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    def apply_filters(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    def paginate(self, query: Query, paginate_strategy: TableDataPaginatingStrategy) -> ListingResponseType:
        pass

    def get_response(self, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        pass
