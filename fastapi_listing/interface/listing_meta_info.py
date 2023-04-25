from typing import Protocol, Type

from fastapi_listing.abstracts import TableDataSortingStrategy, TableDataPaginatingStrategy, QueryStrategy
from fastapi_listing.sorter import SortingOrderStrategy


class ListingMetaInfo(Protocol):

    @property
    def paginating_strategy(self) -> TableDataPaginatingStrategy:  # type:ignore # noqa
        ...

    @property
    def query_strategy(self) -> QueryStrategy:  # type:ignore # noqa
        ...

    @property
    def sorting_column_mapper(self) -> dict:  # type:ignore # noqa
        ...

    @property
    def filter_column_mapper(self) -> dict:  # type:ignore # noqa
        ...

    @property
    def sorting_strategy(self) -> TableDataSortingStrategy:  # type:ignore # noqa
        ...

    @property
    def default_sort_val(self) -> dict[str, str]:  # type:ignore # noqa
        ...

    @property
    def sorter_plugin(self) -> str:  # type:ignore # noqa
        ...

    @property
    def filter_plugin(self) -> str:  # type:ignore # noqa
        ...

    # @property
    # def router_params(self) -> dict:  # type: ignore # noqa
    #     ...

    @property
    def extra_context(self) -> dict: #type: ignore # noqa
        ...


    # where should a protocol file live
