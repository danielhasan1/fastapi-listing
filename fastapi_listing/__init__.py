from fastapi_listing.factory import strategy_factory
from fastapi_listing.strategies import NaiveQueryStrategy, NaivePaginationStrategy, SortingOrderStrategy
from fastapi_listing.service.listing_main import ListingService, FastapiListing
from fastapi_listing.mechanics import IterativeFilterMechanics, SingletonSorterMechanics


__version__ = "0.0.5"

strategy_factory.register_strategy("naive_paginator", NaivePaginationStrategy)
strategy_factory.register_strategy("naive_sorter", SortingOrderStrategy)
strategy_factory.register_strategy("naive_query", NaiveQueryStrategy)
strategy_factory.register_strategy("iterative_filter_mechanics", IterativeFilterMechanics)
strategy_factory.register_strategy("singleton_sorter_mechanics", SingletonSorterMechanics)
