__all__ = [
    "register"
]


import inspect

from fastapi_listing.service import ListingService
from fastapi_listing.factory import filter_factory, _generic_factory, strategy_factory, interceptor_factory
from fastapi_listing.errors import MissingExpectedAttribute
from fastapi_listing.dao import GenericDao


def _validate_strategy_attributes(cls: ListingService):
    if not cls.default_srt_on:
        raise MissingExpectedAttribute("default_srt_on attribute value is not provided! Did you forget to do it?")
    if not strategy_factory.aware_of(cls.query_strategy):
        missing_strategy = cls.query_strategy
    elif not strategy_factory.aware_of(cls.sorting_strategy):
        missing_strategy = cls.sorting_strategy
    elif not strategy_factory.aware_of(cls.paginate_strategy):
        missing_strategy = cls.paginate_strategy
    else:
        missing_strategy = ""
    if missing_strategy:
        raise ValueError(
            f"{cls.__name__} attribute '{missing_strategy}' is not registered/loaded! Did you forget to do it?")
    return True


def _validate_dao_attribute(cls: ListingService):
    if cls.default_dao == GenericDao:
        raise ValueError("Avoid using GenericDao Directly! Extend it!")

    if not inspect.isclass(cls.default_dao):
        raise ValueError("Invalid Dao reference Injected!")

    if not issubclass(cls.default_dao, GenericDao):  # type: ignore
        raise TypeError("Invalid Dao Type! Should Be type of GenericDao")
    return True


def _validate_miscellaneous_attrs(cls: ListingService):
    if not cls.feature_params_adapter:
        raise ValueError("Missing Adapter class for client param conversion!")
    temp = {type(cls.query_strategy), type(cls.sorting_strategy), type(cls.paginate_strategy), type(cls.sort_mecha),
            type(cls.filter_mecha), type(cls.default_srt_ord)}
    if {str} != temp:
        raise TypeError(f"{cls.__name__} has invalid type attribute! Please refer to docs!")
    if cls.default_page_size is None or type(cls.default_page_size) is not int:
        raise ValueError(f"{cls.__name__} has invalid default_page_size attribute!")

    if not cls.default_srt_ord:
        raise ValueError("Missing default_srt_ord attribute!")
    missing_interceptor = ""
    if not interceptor_factory.aware_of(cls.filter_mecha):
        missing_interceptor = cls.filter_mecha
    elif not interceptor_factory.aware_of(cls.sort_mecha):
        missing_interceptor = cls.sort_mecha
    if missing_interceptor:
        raise ValueError(f"{cls.__name__} attribute '{missing_interceptor}' "
                         f"is not registered/loaded! Did you forget to do it?")
    if cls.default_page_size > cls.max_page_size:
        raise ValueError(f"default_page_size {cls.default_page_size!r} can not be greater than max_page_size"
                         f" {cls.max_page_size!r}")


def register():
    def _decorator(cls: ListingService):
        _validate_miscellaneous_attrs(cls)
        _validate_strategy_attributes(cls)
        _validate_dao_attribute(cls)
        filter_mapper = cls.filter_mapper
        sorter_mapper = cls.sort_mapper
        filter_factory.register_filter_mapper(filter_mapper)
        for key, val in sorter_mapper.items():
            if type(val) is tuple:
                _generic_factory.register_sort_mapper(val)
        return cls
    return _decorator
