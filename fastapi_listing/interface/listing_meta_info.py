try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol
from typing import Dict

from fastapi_listing.abstracts import AbsSortingStrategy, AbsPaginatingStrategy, AbsQueryStrategy
from fastapi_listing.interface.client_site_params_adapter import ClientSiteParamAdapter


class ListingMetaInfo(Protocol):
    # paginating_strategy: AbsPaginatingStrategy
    # query_strategy: AbsQueryStrategy
    # sorting_column_mapper: dict
    # filter_column_mapper: dict
    # sorting_strategy: AbsSortingStrategy
    # default_sort_val: Dict[str, str]
    # sorter_mechanic: str
    # filter_mechanic: str
    # extra_context: dict
    # params_adapter: ClientSiteParamAdapter

    @property
    def paginating_strategy(self) -> AbsPaginatingStrategy:  # type : ignore  # noqa
        ...

    @property
    def query_strategy(self) -> AbsQueryStrategy:  # type:ignore # noqa
        ...

    @property
    def sorting_column_mapper(self) -> dict:  # type:ignore # noqa
        ...

    @property
    def filter_column_mapper(self) -> dict:  # type:ignore # noqa
        ...

    @property
    def sorting_strategy(self) -> AbsSortingStrategy:  # type:ignore # noqa
        ...

    @property
    def default_sort_val(self) -> Dict[str, str]:  # type:ignore # noqa
        ...

    @property
    def sorter_mechanic(self) -> str:  # type:ignore # noqa
        ...

    @property
    def filter_mechanic(self) -> str:  # type:ignore # noqa
        ...

    @property
    def extra_context(self) -> dict:  # type: ignore # noqa
        ...

    @property
    def feature_params_adapter(self) -> ClientSiteParamAdapter:  # noqa
        ...

    @property
    def default_page_size(self) -> int:  # noqa
        ...

    # where should a protocol file live
