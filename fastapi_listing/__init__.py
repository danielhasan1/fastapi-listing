from fastapi_listing.factory import strategy_factory
from fastapi_listing.paginator import NaivePaginationStrategy
from fastapi_listing.sorter import SortingOrderStrategy


__version__ = "0.0.1"


strategy_factory.register_strategy("naive_paginator", NaivePaginationStrategy)
strategy_factory.register_strategy("naive_sorter", SortingOrderStrategy)
strategy_factory.register_strategy("naive_query", None) #implement base query
