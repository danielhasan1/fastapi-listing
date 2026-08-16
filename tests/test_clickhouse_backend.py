import json
from urllib.parse import quote

from fastapi_listing import FastapiListing, MetaInfo

from .clickhouse_listing_setup import FakeEmployeeDao, FakeClickHouseClient, register


filter_mapper = register()


def get_url_quoted_string(d):
    return quote(json.dumps(d))


def test_clickhouse_filter_and_sort_reuse_default_strategies():
    """The same EqualityFilter/QueryStrategy/SortingOrderStrategy/PaginationStrategy/
    IterativeFilterInterceptor classes the SQLAlchemy tests use, driving a
    non-ORM raw-SQL backend, unmodified."""
    dao = FakeEmployeeDao(read_db=FakeClickHouseClient())

    resp = FastapiListing(dao=dao, fields_to_fetch=["emp_no", "first_name", "gender"]).get_response(
        MetaInfo(default_srt_on="emp_no", default_srt_ord="asc", filter_mapper=filter_mapper,
                filter=get_url_quoted_string([{"field": "gdr_ch", "value": {"search": "F"}}]))
    )
    assert resp["totalCount"] == 2
    assert {row["gender"] for row in resp["data"]} == {"F"}
    assert [row["emp_no"] for row in resp["data"]] == [3, 4]


def test_clickhouse_sorting_descending():
    dao = FakeEmployeeDao(read_db=FakeClickHouseClient())

    resp = FastapiListing(dao=dao, fields_to_fetch=["emp_no", "first_name", "gender"]).get_response(
        MetaInfo(default_srt_on="emp_no", default_srt_ord="dsc")
    )
    assert [row["emp_no"] for row in resp["data"]] == [4, 3, 2, 1]


def test_clickhouse_context_compiles_parameterized_sql():
    """Values must always flow through the driver's own param binding, never
    be string-formatted into the SQL text."""
    from fastapi_listing.context.clickhouse import ClickHouseQueryContext
    from fastapi_listing.ops import Op

    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees",
                                 columns=["emp_no", "first_name"])
    ctx.where(field="gender", op=Op.EQ, value={"search": "F"})
    sql, params = ctx.compile()
    assert "= 'F'" not in sql and '"F"' not in sql
    assert params == {"__fl_p1": "F"}
    assert "`gender` = %(__fl_p1)s" in sql
