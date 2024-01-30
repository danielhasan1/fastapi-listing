__version__ = "0.3.2"

__all__ = [
    "ListingService",
    "FastapiListing",
    "MetaInfo"
]

from fastapi_listing.factory import strategy_factory, interceptor_factory
from fastapi_listing.strategies import QueryStrategy, PaginationStrategy, SortingOrderStrategy
from fastapi_listing.interceptors import IterativeFilterInterceptor, IndiSorterInterceptor
from fastapi_listing.service.config import MetaInfo
from fastapi_listing.service import ListingService, FastapiListing  # noqa: F401


strategy_factory.register_strategy("default_paginator", PaginationStrategy)
strategy_factory.register_strategy("default_sorter", SortingOrderStrategy)
strategy_factory.register_strategy("default_query", QueryStrategy)
interceptor_factory.register_interceptor("iterative_filter_interceptor", IterativeFilterInterceptor)
interceptor_factory.register_interceptor("indi_sorter_interceptor", IndiSorterInterceptor)



