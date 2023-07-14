from fastapi_listing.service import ListingService
from fastapi_listing.factory import filter_factory, _generic_factory, strategy_factory


def load():
    def _decorator(cls: ListingService):
        filter_mapper = cls.filter_mapper
        sorter_mapper = cls.sort_mapper
        filter_factory.register_filter_mapper(filter_mapper)
        _generic_factory.register_sort_mapper(sorter_mapper)
        # TODO: rest of the loader criteria coming up

