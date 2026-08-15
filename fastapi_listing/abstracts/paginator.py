from abc import ABC, abstractmethod
from typing import Sequence

from fastapi_listing.context import QueryContext
from fastapi_listing.ctyping import BasePage


class AbsPaginatingStrategy(ABC):

    @abstractmethod
    def paginate(self, context: QueryContext, pagination_params: dict,
                 extra_context: dict) -> BasePage:
        pass

    def postprocess(self, rows: Sequence, extra_context: dict) -> Sequence:
        """Hook for post-fetch, non-query business logic (bucket-filling,
        tie-break re-sorting, export-shape reshaping, ...). Identity by
        default; override in a subclass rather than reaching into
        `_get_page`/`_get_page_without_count` or the DAO for this."""
        return rows
