import pytest

from fastapi_listing import FastapiListing, MetaInfo
from fastapi_listing.errors import FastapiListingMigrationError
from fastapi_listing.factory import filter_factory, strategy_factory
from fastapi_listing.filters import generic_filters
from fastapi_listing.strategies import QueryStrategy

from .sqlalchemy_listing_setup import EmployeeDao, session_factory


def test_legacy_filter_signature_raises_clear_migration_error():
    class LegacyFilter(generic_filters.CanonicalFilter):
        # pre-0.4.0 signature: 'query' instead of 'context'
        def filter(self, *, field=None, value=None, query=None):
            return query

    filter_mapper = {"legacy_flt": ("MigrationGuardEmployee.gender", LegacyFilter)}
    filter_factory.register_filter_mapper(filter_mapper)

    dao = EmployeeDao(read_db=session_factory())
    with pytest.raises(FastapiListingMigrationError) as exc:
        FastapiListing(dao=dao, fields_to_fetch=["emp_no"]).get_response(
            MetaInfo(default_srt_on="emp_no",
                    filter_mapper=filter_mapper,
                    filter='%5B%7B%22field%22%3A%20%22legacy_flt%22%2C%20%22value%22%3A%20%7B%22search%22%3A%20%22M%22%7D%7D%5D')
        )
    assert "still uses the pre-0.4.0 'query' parameter" in str(exc.value)
    assert "LegacyFilter" in str(exc.value)


def test_legacy_query_strategy_return_type_raises_clear_migration_error():
    class LegacyQueryStrategy(QueryStrategy):
        def get_query(self, *, request=None, dao=None, extra_context: dict = None):
            # pre-0.4.0 behaviour: returns a raw SQLAlchemy Query, not a QueryContext
            return dao.get_default_read([dao.model.emp_no]).native

    strategy_factory.register_strategy("legacy_query_strategy_test", LegacyQueryStrategy)

    dao = EmployeeDao(read_db=session_factory())
    with pytest.raises(FastapiListingMigrationError) as exc:
        FastapiListing(dao=dao, fields_to_fetch=["emp_no"]).get_response(
            MetaInfo(default_srt_on="emp_no", query_strategy="legacy_query_strategy_test")
        )
    assert "raw" in str(exc.value)
    assert "SqlAlchemyQueryContext" in str(exc.value)
