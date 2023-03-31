from fastapi_listing.factory import strategy_factory
from fastapi_listing.paginator import NaivePaginationStrategy
from fastapi_listing.sorter import AscendingOrderSortingStrategy, DescendingOrderSortingStrategy


__version__ = "0.0.1"


strategy_factory.register_strategy("naive_pagination", NaivePaginationStrategy)
strategy_factory.register_strategy("naive_srt_asc", AscendingOrderSortingStrategy)
strategy_factory.register_strategy("naive_srt_dsc", DescendingOrderSortingStrategy)
strategy_factory.register_strategy("naive_query", None) #implement base query
