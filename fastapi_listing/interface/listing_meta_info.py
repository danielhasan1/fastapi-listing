try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol
from typing import Dict

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi_listing.abstracts import (AbsSortingStrategy, AbsPaginatingStrategy, AbsQueryStrategy,
                                       AbstractListingFeatureParamsAdapter)


class ListingMetaInfo(Protocol):

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
    def default_sort_val(self) -> Dict[str, Literal["asc", "dsc"]]:  # type:ignore # noqa
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
    def feature_params_adapter(self) -> AbstractListingFeatureParamsAdapter:  # noqa
        ...

    @property
    def default_page_size(self) -> int:  # noqa
        ...

    @property
    def max_page_size(self) -> int:  # noqa
        ...

    @property
    def fire_count_qry(self) -> bool: # noqa
        pass
