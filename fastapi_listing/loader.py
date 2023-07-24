import inspect

from fastapi_listing.service import ListingService
from fastapi_listing.factory import filter_factory, _generic_factory, strategy_factory, interceptor_factory
from fastapi_listing.errors import MissingExpectedAttribute
from fastapi_listing.dao import GenericDao

import logging
#
# logger = logging.getLogger()
# # fhandler = logging.FileHandler(filename=r"C:\Users\danis\dev\test.log", mode='a')
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # fhandler.setFormatter(formatter)
# # logger.addHandler(fhandler)
# logger.setLevel(logging.DEBUG)


# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT)
# d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
# logger = logging.getLogger('tcpserver')


def _validate_strategy_attributes(cls: ListingService):
    if not cls.default_srt_on:
        raise MissingExpectedAttribute(f"default_srt_on attribute value is not provided! Did you forget to do it?")
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
        raise ValueError(f"Avoid using GenericDao Directly! Extend it!")

    if not inspect.isclass(cls.default_dao):
        raise ValueError(f"Invalid Dao reference Injected!")

    if not issubclass(cls.default_dao, GenericDao):  # type: ignore
        raise TypeError(f"Invalid Dao Type! Should Be type of GenericDao")
    return True


def _validate_miscellaneous_attrs(cls: ListingService):
    if not cls.feature_params_adapter:
        raise ValueError(f"Missing Adapter class for client param conversion!")
    temp = {type(cls.query_strategy), type(cls.sorting_strategy), type(cls.paginate_strategy), type(cls.sort_mecha),
            type(cls.filter_mecha), type(cls.default_srt_ord)}
    if {str} != temp:
        raise TypeError(f"{cls.__name__} has invalid type attribute! Please refer to docs!")
    if cls.default_page_size is None or type(cls.default_page_size) is not int:
        raise ValueError(f"{cls.__name__} has invalid default_page_size attribute!")

    if not cls.default_srt_ord:
        raise ValueError(f"Missing default_srt_ord attribute!")
    missing_interceptor = ""
    if not interceptor_factory.aware_of(cls.filter_mecha):
        missing_interceptor = cls.filter_mecha
    elif not interceptor_factory.aware_of(cls.sort_mecha):
        missing_interceptor = cls.sort_mecha
    if missing_interceptor:
        raise ValueError(f"{cls.__name__} attribute '{missing_interceptor}' "
                         f"is not registered/loaded! Did you forget to do it?")


def register():
    def _decorator(cls: ListingService):
        filter_mapper = cls.filter_mapper
        sorter_mapper = cls.sort_mapper
        filter_factory.register_filter_mapper(filter_mapper)
        for key, val in sorter_mapper.items():
            if type(val) is tuple:
                _generic_factory.register_sort_mapper(val)
        _validate_miscellaneous_attrs(cls)
        _validate_strategy_attributes(cls)
        _validate_dao_attribute(cls)
        return cls
    return _decorator





