from typing import Protocol, Type

from fastapi_listing.abstracts import TableDataSortingStrategy, TableDataPaginatingStrategy, QueryStrategy


class ListingMetaInfo(Protocol):

    @property
    def sorting_strategy(self):
        ...

    @property
    def paginating_strategy(self) -> TableDataPaginatingStrategy:
        ...

    @property
    def query_strategy(self) -> QueryStrategy:
        ...

    @property
    def sorting_column_mapper(self) -> dict:
        ...

    @property
    def filter_column_mapper(self) -> dict:
        ...

#where should a protocol file live
