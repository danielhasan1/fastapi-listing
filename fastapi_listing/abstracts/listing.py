from sqlalchemy.orm import Query
from abc import ABC
from typing import Type

from fastapi_listing.abstracts import ListingMetaInfo, TableDataSortingStrategy, \
    TableDataPaginatingStrategy
from fastapi_listing.typing import ListingResponseType


class ListingBase(ABC):

    def prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        pass

    def apply_sorting(self, query: Query, sorting_strategy: TableDataSortingStrategy,
                      sort_field_mapper: dict[str, str]) -> Query:
        pass

    def apply_filters(self, query: Query, filter_field_mapper: dict[str, str]) -> Query:
        pass

    def paginate(self, query: Query, paginate_strategy: TableDataPaginatingStrategy) -> ListingResponseType:
        pass

    def get_response(self, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        pass