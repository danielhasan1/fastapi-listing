from fastapi_listing.factory import strategy_factory
from fastapi_listing.strategies import NaiveQueryStrategy, NaivePaginationStrategy, SortingOrderStrategy
from fastapi_listing.service.listing_main import ListingService, FastapiListing


__version__ = "0.0.3"

strategy_factory.register_strategy("naive_paginator", NaivePaginationStrategy)
strategy_factory.register_strategy("naive_sorter", SortingOrderStrategy)
strategy_factory.register_strategy("naive_query", NaiveQueryStrategy)
