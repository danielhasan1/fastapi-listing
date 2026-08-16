"""Real-server validation for the ClickHouse backend - not a fake client.

tests/test_clickhouse_backend.py and test_query_context.py prove the Python
logic is internally consistent (right SQL shape, right params) against a fake
client that pattern-matches expected output. This file proves the generated
SQL is actually valid ClickHouse dialect, executed by the real
`clickhouse-driver` package against a real server - CTEs/derived-table
wrapping, GROUP BY + HAVING, and parameter binding all behave as expected on
a real engine, not just in a regex-matching fake.

In CI (see .github/workflows/tests.yml), a real `clickhouse/clickhouse-server`
container is always provisioned, so this always runs there. Locally, it skips
gracefully if nothing is listening on the configured host/port - run
`docker compose -f docker-compose.dev.yml up -d clickhouse` (or point
FASTAPI_LISTING_TEST_CLICKHOUSE_HOST/PORT at your own instance) to exercise it.
"""

import os

import pytest

clickhouse_driver = pytest.importorskip("clickhouse_driver", reason="clickhouse-driver not installed")

from fastapi_listing import FastapiListing, MetaInfo
from fastapi_listing.context.clickhouse import ClickHouseQueryContext
from fastapi_listing.dao import ClickHouseDao
from fastapi_listing.factory import filter_factory
from fastapi_listing.filters import generic_filters
from fastapi_listing.ops import Op

CH_HOST = os.environ.get("FASTAPI_LISTING_TEST_CLICKHOUSE_HOST", "127.0.0.1")
CH_PORT = int(os.environ.get("FASTAPI_LISTING_TEST_CLICKHOUSE_PORT", "9010"))
DB_NAME = "fastapi_listing_integration_test"


def _make_client():
    return clickhouse_driver.Client(host=CH_HOST, port=CH_PORT, connect_timeout=3)


@pytest.fixture(scope="module")
def real_client():
    try:
        client = _make_client()
        client.execute("SELECT 1")
    except Exception as exc:
        pytest.skip(f"No real ClickHouse reachable at {CH_HOST}:{CH_PORT} ({exc})")
        return

    client.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    client.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_NAME}.employees (
            emp_no UInt32, first_name String, gender String
        ) ENGINE = MergeTree() ORDER BY emp_no
    """)
    client.execute(f"TRUNCATE TABLE {DB_NAME}.employees")
    client.execute(f"INSERT INTO {DB_NAME}.employees VALUES", [
        (1, "Sachin", "M"), (2, "Rahul", "M"), (3, "Anjali", "F"), (4, "Priya", "F"),
    ])
    client.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_NAME}.site_metrics_weekly (
            account_id UInt32, site_id UInt32, site String,
            time_value UInt32, indexed_pages UInt64
        ) ENGINE = MergeTree() ORDER BY (account_id, site_id, time_value)
    """)
    client.execute(f"TRUNCATE TABLE {DB_NAME}.site_metrics_weekly")
    client.execute(f"INSERT INTO {DB_NAME}.site_metrics_weekly VALUES", [
        (1, 10, "brightedge-like.example", 1, 5000), (1, 10, "brightedge-like.example", 2, 4500),
        (1, 20, "another.example", 1, 1200), (1, 20, "another.example", 2, 1300),
        (1, 30, "third.example", 1, 300), (1, 30, "third.example", 2, 250),
    ])
    yield client
    client.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")


class _Employee:
    __table__ = f"{DB_NAME}.employees"
    emp_no = "emp_no"
    first_name = "first_name"
    gender = "gender"


class _EmployeeDao(ClickHouseDao):
    name = "real_ch_integration_employee"
    model = _Employee


def test_canonical_filter_sort_paginate_against_real_clickhouse(real_client):
    # "RealCHIntegration.gender", not "Employee.gender" - filter_factory registers by field path, not
    # alias, and "Employee.gender" is already registered by tests/service_setup.py. extract_field() only
    # reads the segment after the last dot, so this still resolves to the "gender" attribute correctly.
    filter_mapper = {"gdr_real_ch": ("RealCHIntegration.gender", generic_filters.EqualityFilter)}
    filter_factory.register_filter_mapper(filter_mapper)

    import json
    from urllib.parse import quote
    filter_qs = quote(json.dumps([{"field": "gdr_real_ch", "value": {"search": "F"}}]))

    dao = _EmployeeDao(read_db=real_client)
    resp = FastapiListing(dao=dao, fields_to_fetch=["emp_no", "first_name", "gender"]).get_response(
        MetaInfo(default_srt_on="emp_no", default_srt_ord="asc", filter_mapper=filter_mapper, filter=filter_qs)
    )
    assert resp["totalCount"] == 2
    assert [row["emp_no"] for row in resp["data"]] == [3, 4]


def test_having_against_a_real_group_by(real_client):
    ctx = ClickHouseQueryContext(client=real_client, table=f"{DB_NAME}.employees", columns=["gender"])
    ctx.where(field="gender", op=Op.GROUP_BY, value=None)
    ctx.having(field="gender", op=Op.EQ, value={"search": "M"})
    assert ctx.fetch() == [{"gender": "M"}]


def test_grouped_count_wraps_correctly_on_a_real_server(real_client):
    ctx = ClickHouseQueryContext(client=real_client, table=f"{DB_NAME}.employees", columns=["gender"])
    ctx.where(field="gender", op=Op.GROUP_BY, value=None)
    assert ctx.count() == 2  # 2 distinct genders, not "2 rows in the M group + 2 in the F group"


def test_from_raw_sql_aggregation_against_a_real_server(real_client):
    raw_sql = f"""
        SELECT site_id, any(site) AS domain,
            sumIf(indexed_pages, time_value = 1) AS indexed_pages_current,
            sumIf(indexed_pages, time_value = 2) AS indexed_pages_prev
        FROM {DB_NAME}.site_metrics_weekly
        WHERE account_id = %(account_id)s
        GROUP BY site_id
    """
    ctx = ClickHouseQueryContext.from_raw_sql(client=real_client, sql=raw_sql, params={"account_id": 1})
    ctx.where(field="indexed_pages_current", op=Op.GT, value={"search": 1000})
    ctx.order_by_raw("(site_id = 10) DESC, `indexed_pages_current` DESC")
    ctx.limit_offset(limit=10, offset=0)

    rows = ctx.fetch()
    assert {row["site_id"] for row in rows} == {10, 20}
    assert rows[0]["site_id"] == 10  # pinned first regardless of the metric sort
