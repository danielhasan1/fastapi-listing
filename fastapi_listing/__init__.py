from fastapi_listing.factory import strategy_factory, interceptor_factory
from fastapi_listing.strategies import QueryStrategy, PaginationStrategy, SortingOrderStrategy
from fastapi_listing.service import ListingService, FastapiListing
from fastapi_listing.interceptors import IterativeFilterInterceptor, IndiSorterInterceptor


__version__ = "0.2.1"

strategy_factory.register_strategy("default_paginator", PaginationStrategy)
strategy_factory.register_strategy("default_sorter", SortingOrderStrategy)
strategy_factory.register_strategy("default_query", QueryStrategy)
interceptor_factory.register_interceptor("iterative_filter_interceptor", IterativeFilterInterceptor)
interceptor_factory.register_interceptor("indi_sorter_interceptor", IndiSorterInterceptor)
