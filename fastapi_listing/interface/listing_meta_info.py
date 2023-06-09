try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol
from typing import Dict

from fastapi_listing.abstracts import AbsSortingStrategy, AbsPaginatingStrategy, AbsQueryStrategy


class ListingMetaInfo(Protocol):

    @property
    def paginating_strategy() -> AbsPaginatingStrategy:  # type:ignore # noqa
        ...

    @property
    def query_strategy() -> AbsQueryStrategy:  # type:ignore # noqa
        ...

    @property
    def sorting_column_mapper() -> dict:  # type:ignore # noqa
        ...

    @property
    def filter_column_mapper() -> dict:  # type:ignore # noqa
        ...

    @property
    def sorting_strategy() -> AbsSortingStrategy:  # type:ignore # noqa
        ...

    @property
    def default_sort_val() -> Dict[str, str]:  # type:ignore # noqa
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
    def extra_context() -> dict:  # type: ignore # noqa
        ...

    # where should a protocol file live
