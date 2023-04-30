from typing import Protocol, Type

from fastapi_listing.abstracts import TableDataSortingStrategy, TableDataPaginatingStrategy, QueryStrategy
from fastapi_listing.sorter import SortingOrderStrategy


class ListingMetaInfo(Protocol):

    @property
    def paginating_strategy() -> TableDataPaginatingStrategy:  # type:ignore # noqa
        ...

    @property
    def query_strategy() -> QueryStrategy:  # type:ignore # noqa
        ...

    @property
    def sorting_column_mapper() -> dict:  # type:ignore # noqa
        ...

    @property
    def filter_column_mapper() -> dict:  # type:ignore # noqa
        ...

    @property
    def sorting_strategy() -> TableDataSortingStrategy:  # type:ignore # noqa
        ...

    @property
    def default_sort_val() -> dict[str, str]:  # type:ignore # noqa
        ...

    @property
    def sorter_mechanic() -> str:  # type:ignore # noqa
        ...

    @property
    def filter_mechanic() -> str:  # type:ignore # noqa
        ...

    # @property
    # def router_params(self) -> dict:  # type: ignore # noqa
    #     ...

    @property
    def extra_context() -> dict: #type: ignore # noqa
        ...


    # where should a protocol file live
