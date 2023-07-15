from fastapi_listing.factory import strategy_factory
from fastapi_listing.strategies import QueryStrategy, PaginationStrategy, SortingOrderStrategy
from fastapi_listing.service import ListingService, FastapiListing
from fastapi_listing.mechanics import IterativeFilterMechanics, SingletonSorterMechanics


__version__ = "0.1.0"

strategy_factory.register_strategy("default_paginator", PaginationStrategy)
strategy_factory.register_strategy("default_sorter", SortingOrderStrategy)
strategy_factory.register_strategy("default_query", QueryStrategy)
strategy_factory.register_strategy("iterative_filter_mechanics", IterativeFilterMechanics)
strategy_factory.register_strategy("singleton_sorter_mechanics", SingletonSorterMechanics)
