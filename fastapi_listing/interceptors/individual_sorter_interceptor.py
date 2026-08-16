from typing import List, Dict

from fastapi_listing.abstracts import AbstractSorterInterceptor
from fastapi_listing.errors import guard_legacy_signature
from fastapi_listing.sorter import SortingOrderStrategy
from fastapi_listing.context import QueryContext


class IndiSorterInterceptor(AbstractSorterInterceptor):
    """
    Singleton Sorter mechanic.
        # ideally sorting should only happen on one field multi field sorting puts
        # unwanted strain on table when the size is big and not really popular
        # among various clients. Still leaving room for extension won't hurt
        # by default even if client is sending multiple sorting params we prioritize
        # the latest one which is last column that client requested to sort on.
        # if user want they can implement their own asc or dsc sorting order strategy and
        # decide how they really want to apply sorting params maybe all maybe none or maybe
        # conditional sorting where if one param is applied then don't apply another specific one, etc.
    """

    def apply(self, *, context: QueryContext = None, strategy: SortingOrderStrategy = None,
              sorting_params: List[Dict[str, str]] = None, extra_context: dict = None) -> QueryContext:
        latest = sorting_params[-1]
        guard_legacy_signature(
            strategy.sort, legacy_kwarg="query", new_kwarg="context",
            subject=f"Custom sorting strategy {type(strategy).__name__!r}",
            fix="Rename its 'query' parameter to 'context'; delegate to context.order_by(...) "
                "instead of calling .order_by() directly.")
        context = strategy.sort(context=context, value=latest, extra_context=extra_context)
        return context
