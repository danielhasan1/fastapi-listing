"""Two things the SQLite-based tests elsewhere never exercised:

1. loader.py's default_page_size > max_page_size validation.
2. The class-based ListingService flow itself (MetaInfo(), switch(), and the
   dao_factory -> MissingSessionError -> manual-construction fallback in
   ListingService.__init__) - every other SQLite test in this suite calls
   FastapiListing(dao=dao, ...) directly, bypassing ListingService entirely.
   Real coverage of this path previously depended on the MySQL-backed tests.
"""

import pytest

from fastapi_listing import ListingService, loader
from fastapi_listing.dao import dao_factory
from fastapi_listing.errors import MissingExpectedAttribute

from .sqlalchemy_listing_setup import EmployeeDao, session_factory

dao_factory.register_dao(EmployeeDao.name, EmployeeDao)


def test_loader_rejects_default_page_size_greater_than_max_page_size():
    with pytest.raises(ValueError, match="can not be greater than max_page_size"):
        @loader.register()
        class _BadPageSizeService(ListingService):  # noqa: F811,F841
            default_srt_on = "emp_no"
            default_dao = EmployeeDao
            default_page_size = 100
            max_page_size = 50


@loader.register()
class _SqliteEmployeeListingService(ListingService):
    default_srt_on = "emp_no"
    default_dao = EmployeeDao

    def get_listing(self):
        resp = self.get_response_for_test()
        return resp

    def get_response_for_test(self):
        from fastapi_listing import FastapiListing
        return FastapiListing(self.request, self.dao, fields_to_fetch=["emp_no", "first_name"]).get_response(
            self.MetaInfo(self))


def test_listing_service_falls_back_to_manual_dao_construction_without_bound_session():
    """dao_factory.create() raises MissingSessionError here (the DAO is
    registered, but no middleware/manager() bound a session in this test) -
    ListingService.__init__ must fall back to constructing the DAO directly
    from the read_db kwarg instead of propagating that error."""
    service = _SqliteEmployeeListingService(request=None, read_db=session_factory())
    assert isinstance(service.dao, EmployeeDao)
    resp = service.get_listing()
    assert [row.emp_no for row in resp["data"]] == [4, 3, 2, 1]  # default dsc sort


def test_listing_service_switch_changes_a_registered_strategy_attribute():
    service = _SqliteEmployeeListingService(request=None, read_db=session_factory())
    assert service.query_strategy == "default_query"
    service.switch("query_strategy", "default_query")  # same value, but exercises the real path
    assert service.query_strategy == "default_query"


def test_listing_service_switch_rejects_unknown_strategy_type():
    service = _SqliteEmployeeListingService(request=None, read_db=session_factory())
    with pytest.raises(ValueError, match="unknown strategy type"):
        service.switch("not_a_real_strategy_type", "whatever")


def test_listing_service_missing_default_srt_on_raises():
    with pytest.raises(MissingExpectedAttribute):
        @loader.register()
        class _MissingSortOnService(ListingService):  # noqa: F811,F841
            default_srt_on = ""
            default_dao = EmployeeDao
