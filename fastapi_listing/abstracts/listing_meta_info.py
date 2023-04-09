from typing import Protocol, Type

from fastapi_listing.abstracts import TableDataSortingStrategy, TableDataPaginatingStrategy, QueryStrategy
from fastapi_listing.sorter import SortingOrderStrategy


class ListingMetaInfo(Protocol):

    # @property
    # def sorting_strategy(self) -> TableDataSortingStrategy:
    #     ...

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

    @property
    def sorting_strategy(self) -> TableDataSortingStrategy:
        ...

    @property
    def default_sort_val(self) -> dict[str, str]:
        ...

    @property
    def sorter_plugins(self) -> list[str]:
        ...

    @property
    def filter_plugins(self) -> list[str]:
        ...

#where should a protocol file live
