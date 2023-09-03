from fastapi import FastAPI
import pytest
from .fake_listing_setup import  \
    spawn_valueerror_for_strategy_registry, spawn_valueerror_for_filter_factory, invalid_type_factory_keys
from .test_main_v2 import get_db
import types

app = FastAPI()


def test_strategy_factory_unique_strategy_register():
    with pytest.raises(ValueError) as e:
        spawn_valueerror_for_strategy_registry("same_strategy_key", "same_strategy_key")
    assert e.value.args[0] == "strategy name: same_strategy_key, already in use with FakePaginationStrategyV2!"


def test_filter_factory_unique_strategy_register():
    with pytest.raises(ValueError) as e:
        spawn_valueerror_for_filter_factory("same_field_name", "same_field_name")
    assert e.value.args[0] == "filter key 'same_field_name' already in use with 'EqualityFilter'"


def test_factory_key_inputs():
    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("filter", None)
    assert e.value.args[0] == "Invalid type key!"

    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("filter", "")
    assert e.value.args[0] == "Invalid type key!"

    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("strategy", None)
    assert e.value.args[0] == "Invalid type key!"

    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("strategy", "")
    assert e.value.args[0] == "Invalid type key!"


def test_dao_factory_errors():
    from fastapi_listing.dao import dao_factory
    from fastapi_listing.errors import MissingSessionError
    from .dao_setup import TitleDao
    with pytest.raises(ValueError) as e:
        dao_factory.register_dao(None, None)
    assert e.value.args[0] == "Invalid type key, expected str type got <class 'NoneType'> for None!"
    dao_factory.register_dao("titlepre", TitleDao)
    with pytest.raises(ValueError) as e:
        dao_factory.register_dao("titlepre", None)
    assert e.value.args[0] == "Dao name titlepre already in use with TitleDao!"
    with pytest.raises(ValueError) as e:
        dao_factory.create(None)
    assert e.value.args[0] is None

    with pytest.raises(MissingSessionError) as e:
        dao_factory.create("titlepre")
    assert e.value.args[0] == """
        No session found! Either you are not currently in a request context,
        or you need to manually create a session context and pass the callable to middleware args
        e.g.
        callable -> get_db
        app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)
        or
        pass a db session manually to your listing service
        e.g.
        AbcListingService(read_db=sqlalchemysession)
        """


def test_dao_factory_working():

    from fastapi_listing.dao import dao_factory
    from fastapi_listing.middlewares import manager
    from .dao_setup import TitleDao
    with manager(read_ses=get_db, master=get_db, implicit_close=True, suppress_warnings=False):
        dao_factory.register_dao("title_2", TitleDao)
        both_dao: TitleDao = dao_factory.create("title_2", both=True)
        assert both_dao.get_emp_title_by_id(10001) == "Senior Engineer"
        del both_dao
        master_dao: TitleDao = dao_factory.create("title_2", master=True)
        assert master_dao.get_emp_title_by_id_from_master(10001) == "Senior Engineer"
        del master_dao

        with pytest.raises(ValueError) as e:
            dao_factory.create("title_2", replica=False)
        assert e.value.args[0] == "Invalid creation type for dao object allowed types 'replica', 'master', or 'both'"


def test_generic_factory_for_semantics_sorter():
    from fastapi_listing.factory import _generic_factory
    _generic_factory.register("test", lambda x: x)  # testing callable example
    with pytest.raises(ValueError) as e:
        _generic_factory.register("test", lambda x: x)
    assert e.value.args[0] == "Factory can not have duplicate builder key test for instance <lambda>"
    # checking sort mapper registerer and validator
    sort_mapper = {"test_key": "column_1"}
    with pytest.raises(ValueError) as e:
        _generic_factory.register_sort_mapper(sort_mapper)
    assert e.value.args[0] == "Invalid sorter mapper semantic! Expected tuple!"

    sort_val = ("test",)
    with pytest.raises(ValueError) as e:
        _generic_factory.register_sort_mapper(sort_val)
    assert e.value.args[0] == "Invalid sorter mapper semantic ('test',)! min tuple length should be 2."

    sort_val = (1, 1)
    with pytest.raises(ValueError) as e:
        _generic_factory.register_sort_mapper(sort_val)
    assert e.value.args[0] == "Invalid sorter mapper semantic (1, 1)! first tuple element should be field (str)"

    sort_val = ("test", "test")
    with pytest.raises(ValueError) as e:
        _generic_factory.register_sort_mapper(sort_val)
    assert e.value.args[0] == "positional arg error, expects a callable but received: test!"

    with pytest.raises(ValueError) as e:
        _generic_factory.create("abc")
    assert e.value.args[0] == "unknown character type 'abc'"


def test_filter_factory_semantics():
    from fastapi_listing import ListingService, loader
    from .dao_setup import TitleDao

    # when filter mapper is not having tuple val
    with pytest.raises(ValueError) as e:
        @loader.register()
        class ABCListing(ListingService):  # noqa: F811,F841
            default_srt_on = "test"
            filter_mapper = {
                "test": "abc"
            }
            default_dao = TitleDao
    assert e.value.args[0] == "Invalid filter mapper semantic! Expected tuple!"

    # when filter mapper having incorrect length
    with pytest.raises(ValueError) as e:
        @loader.register()
        class ABCListing(ListingService):  # noqa: F811,F841
            default_srt_on = "test"
            filter_mapper = {
                "test": ("abc",)
            }
            default_dao = TitleDao
    assert e.value.args[0] == "Invalid filter mapper semantic ('abc',)! min tuple length should be 2."

    # checking args
    with pytest.raises(ValueError) as e:
        @loader.register()
        class ABCListing(ListingService):  # noqa: F811,F841
            default_srt_on = "test"
            filter_mapper = {
                "test": (1, "test")
            }
            default_dao = TitleDao

    assert e.value.args[0] == "Invalid filter mapper semantic (1, 'test')! first tuple element should be field (str)"

    # checking args
    with pytest.raises(ValueError) as e:
        @loader.register()
        class ABCListing(ListingService):  # noqa: F811,F841
            default_srt_on = "test"
            filter_mapper = {
                "test": ("test", "test")
            }
            default_dao = TitleDao

    assert e.value.args[0] == "Invalid filter mapper semantic 'test'! Expects a class!"

    # checking args
    with pytest.raises(ValueError) as e:
        @loader.register()
        class ABCListing(ListingService):  # noqa: F811,F841
            default_srt_on = "test"
            filter_mapper = {
                "test": ("test", object)
            }
            default_dao = TitleDao

    assert e.value.args[0] == "Invalid filter mapper semantic <class 'object'>! Expects a subclass of CommonFilterImpl"

    # checking args
    with pytest.raises(ValueError) as e:
        from fastapi_listing.filters import generic_filters

        @loader.register()
        class ABCListing(ListingService):  # noqa: F811,F841
            default_srt_on = "test"
            filter_mapper = {
                "test": ("test", generic_filters.EqualityFilter, 1)
            }
            default_dao = TitleDao

    assert e.value.args[0] == "positional arg error, expects a callable but received: 1!"

    # check create error
    from fastapi_listing.factory import filter_factory

    with pytest.raises(ValueError) as e:
        filter_factory.create("test_unknown")
    assert e.value.args[0] == "filter factory couldn't find registered key 'test_unknown'"


def test_interceptor_factory():
    from fastapi_listing.factory import interceptor_factory
    from fastapi_listing.interceptors import IterativeFilterInterceptor

    with pytest.raises(ValueError) as e:
        interceptor_factory.register_interceptor(1, object)
    assert e.value.args[0] == "Invalid type key!"
    with pytest.raises(ValueError) as e:
        interceptor_factory.register_interceptor("test", IterativeFilterInterceptor)
        interceptor_factory.register_interceptor("test", IterativeFilterInterceptor)
    assert e.value.args[0] == "interceptor name 'test', already in use with 'IterativeFilterInterceptor'!"
    with pytest.raises(ValueError) as e:
        interceptor_factory.register_interceptor("test2", "abc")
    assert e.value.args[0] == "'abc' is not a valid class!"

    with pytest.raises(ValueError) as e:
        interceptor_factory.create("unknown_interceptor")
    assert e.value.args[0] == "interceptor factory couldn't find register key 'unknown_interceptor'"

    with pytest.raises(ValueError) as e:
        interceptor_factory.register_interceptor("testtest", object)
    assert e.value.args[0] == ("Invalid interceptor class, expects a subclass of either "
                               "'AbstractSorterInterceptor' or 'AbstractFilterInterceptor'")


# write test for strategy class
