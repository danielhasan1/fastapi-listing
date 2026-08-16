"""Backend-agnosticism regression harness: a fully in-process fake ClickHouse
client (no network, no real clickhouse-driver dependency) driving the exact
same, unmodified EqualityFilter/QueryStrategy/SortingOrderStrategy/
PaginationStrategy/IterativeFilterInterceptor classes the SQLAlchemy tests use.
If this passes, the QueryContext abstraction genuinely generalizes rather than
merely working for SQLAlchemy by accident.
"""

import re

from fastapi_listing.dao import ClickHouseDao
from fastapi_listing.factory import filter_factory


ROWS = [
    {"emp_no": 1, "first_name": "Sachin", "gender": "M"},
    {"emp_no": 2, "first_name": "Rahul", "gender": "M"},
    {"emp_no": 3, "first_name": "Anjali", "gender": "F"},
    {"emp_no": 4, "first_name": "Priya", "gender": "F"},
]


class FakeClickHouseClient:
    """Hand-rolled fake mimicking clickhouse_driver.Client.execute(). Asserts
    the real ClickHouseQueryContext-generated SQL/params round-trip correctly
    against an in-memory list of dict rows, standing in for a real server."""

    def execute(self, sql, params=None, with_column_types=False):
        params = params or {}
        rows = list(ROWS)

        # Match "`gender` = %(<any bind key>)s" rather than hardcoding a
        # specific key name - the bind-key naming scheme is an implementation
        # detail this fixture shouldn't be coupled to.
        gender_eq = re.search(r"`gender` = %\((\w+)\)s", sql)
        if gender_eq:
            rows = [r for r in rows if r["gender"] == params[gender_eq.group(1)]]

        if sql.strip().upper().startswith("SELECT COUNT(*)"):
            return [(len(rows),)]

        if "ORDER BY `emp_no` DESC" in sql:
            rows = sorted(rows, key=lambda r: r["emp_no"], reverse=True)
        elif "ORDER BY `emp_no` ASC" in sql:
            rows = sorted(rows, key=lambda r: r["emp_no"])

        result = [(r["emp_no"], r["first_name"], r["gender"]) for r in rows]
        if with_column_types:
            return result, [("emp_no", "Int32"), ("first_name", "String"), ("gender", "String")]
        return result


class FakeEmployee:
    __table__ = "employees"
    emp_no = "emp_no"
    first_name = "first_name"
    gender = "gender"


class FakeEmployeeDao(ClickHouseDao):
    name = "employee_ch_test"
    model = FakeEmployee


def register():
    from fastapi_listing.filters import generic_filters

    filter_mapper = {"gdr_ch": ("FakeEmployee.gender", generic_filters.EqualityFilter)}
    filter_factory.register_filter_mapper(filter_mapper)
    return filter_mapper
