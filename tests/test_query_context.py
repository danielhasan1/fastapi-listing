"""Op-dispatch coverage for both QueryContext implementations, the
CommonFilterImpl deprecation alias, and the PaginationStrategy.postprocess
hook - the pieces the smoke-tested-but-uncommitted scripts were covering
during development.
"""

import warnings

import pytest

from fastapi_listing import FastapiListing, MetaInfo
from fastapi_listing.context.clickhouse import ClickHouseQueryContext
from fastapi_listing.context.sqlalchemy import SqlAlchemyQueryContext
from fastapi_listing.dao import GenericDao
from fastapi_listing.filters import generic_filters
from fastapi_listing.ops import Op
from fastapi_listing.paginator import PaginationStrategy
from fastapi_listing.factory import strategy_factory

from .clickhouse_listing_setup import FakeClickHouseClient
from .sqlalchemy_listing_setup import Employee, EmployeeDao, session_factory


# ---------- SqlAlchemyQueryContext: every Op against a real SQLAlchemy Query ----------

@pytest.mark.parametrize("op,value,expected_emp_nos", [
    (Op.EQ, {"search": "M"}, {1, 2}),
    (Op.NEQ, {"search": "M"}, {3, 4}),
    (Op.IN, {"list": ["M"]}, {1, 2}),
    (Op.LIKE, {"search": "M"}, {1, 2}),
    (Op.STARTS_WITH, {"search": "M"}, {1, 2}),
    (Op.ENDS_WITH, {"search": "M"}, {1, 2}),
    (Op.CONTAINS, {"search": "M"}, {1, 2}),
])
def test_sqlalchemy_context_gender_ops(op, value, expected_emp_nos):
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    ctx.where(field=Employee.gender, op=op, value=value)
    assert {row.emp_no for row in ctx.fetch()} == expected_emp_nos


def test_sqlalchemy_context_range():
    from datetime import date
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    ctx.where(field=Employee.hire_date, op=Op.RANGE,
              value={"start": date(1990, 1, 1), "end": date(1996, 1, 1)})
    assert {row.emp_no for row in ctx.fetch()} == {1, 2}


@pytest.mark.parametrize("op", [Op.GT, Op.GTE, Op.LT, Op.LTE])
def test_sqlalchemy_context_comparison_ops_run_without_error(op):
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    ctx.where(field=Employee.emp_no, op=op, value={"search": 2})
    assert isinstance(ctx.fetch(), list)


def test_sqlalchemy_context_is_null_and_not_null():
    session = session_factory()
    assert len(SqlAlchemyQueryContext(session.query(Employee)).where(
        field=Employee.gender, op=Op.NOT_NULL, value=None).fetch()) == 4
    assert len(SqlAlchemyQueryContext(session.query(Employee)).where(
        field=Employee.gender, op=Op.IS_NULL, value=None).fetch()) == 0


def test_sqlalchemy_context_group_by_and_distinct_run_without_error():
    session = session_factory()
    SqlAlchemyQueryContext(session.query(Employee.gender)).where(
        field=Employee.gender, op=Op.GROUP_BY, value=None).fetch()
    with warnings.catch_warnings():
        # SQLite (unlike the library's real MySQL target) warns that
        # DISTINCT-on-a-column is Postgres-only syntax and is otherwise
        # silently ignored - a pre-existing SQLAlchemy quirk, not a
        # regression, so it's suppressed here rather than asserted on.
        warnings.simplefilter("ignore")
        SqlAlchemyQueryContext(session.query(Employee.gender)).where(
            field=Employee.gender, op=Op.DISTINCT, value=None).fetch()


def test_sqlalchemy_context_having_filters_on_aggregated_field():
    from sqlalchemy import func
    session = session_factory()

    # 2 groups of 2 (M, F) - HAVING count(*) >= 2 keeps both, > 2 keeps none.
    ctx = SqlAlchemyQueryContext(session.query(Employee.gender, func.count(Employee.emp_no)))
    ctx.where(field=Employee.gender, op=Op.GROUP_BY, value=None)
    ctx.having(field=func.count(Employee.emp_no), op=Op.GTE, value={"search": 2})
    assert {row[0] for row in ctx.fetch()} == {"M", "F"}

    ctx2 = SqlAlchemyQueryContext(session.query(Employee.gender, func.count(Employee.emp_no)))
    ctx2.where(field=Employee.gender, op=Op.GROUP_BY, value=None)
    ctx2.having(field=func.count(Employee.emp_no), op=Op.GT, value={"search": 2})
    assert ctx2.fetch() == []


def test_sqlalchemy_context_unsupported_op_raises():
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    with pytest.raises(ValueError):
        ctx.where(field=Employee.gender, op="not-a-real-op", value={"search": "M"})


def test_sqlalchemy_context_having_unsupported_op_raises():
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    with pytest.raises(ValueError):
        ctx.having(field=Employee.gender, op="not-a-real-op", value={"search": "M"})


def test_sqlalchemy_context_native_and_with_native_roundtrip():
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    mutated = ctx.native.filter(Employee.emp_no == 1)
    ctx = ctx.with_native(mutated)
    assert [row.emp_no for row in ctx.fetch()] == [1]


def test_sqlalchemy_context_order_by_and_limit_offset_and_count():
    session = session_factory()
    ctx = SqlAlchemyQueryContext(session.query(Employee))
    assert ctx.count() == 4
    ctx.order_by(field=Employee.emp_no, direction="dsc")
    ctx.limit_offset(limit=2, offset=0)
    assert [row.emp_no for row in ctx.fetch()] == [4, 3]


# ---------- ClickHouseQueryContext: every Op, plus compile()/count_compile() ----------

@pytest.mark.parametrize("op,value", [
    (Op.EQ, {"search": "F"}),
    (Op.NEQ, {"search": "F"}),
    (Op.IN, {"list": ["F"]}),
    (Op.RANGE, {"start": 1, "end": 2}),
    (Op.LIKE, {"search": "F"}),
    (Op.STARTS_WITH, {"search": "F"}),
    (Op.ENDS_WITH, {"search": "F"}),
    (Op.CONTAINS, {"search": "F"}),
    (Op.GT, {"search": 1}),
    (Op.GTE, {"search": 1}),
    (Op.LT, {"search": 4}),
    (Op.LTE, {"search": 4}),
    (Op.IS_NULL, None),
    (Op.NOT_NULL, None),
])
def test_clickhouse_context_every_op_compiles_and_binds_params(op, value):
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees",
                                 columns=["emp_no"])
    ctx.where(field="gender", op=op, value=value)
    sql, params = ctx.compile()
    assert "employees" in sql
    if value and value.get("search") is not None:
        assert any(str(value["search"]) in str(bound) for bound in params.values())


def test_clickhouse_context_group_by_and_distinct():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees", columns=["gender"])
    ctx.where(field="gender", op=Op.GROUP_BY, value=None)
    sql, _ = ctx.compile()
    assert "GROUP BY `gender`" in sql

    ctx2 = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees", columns=["gender"])
    ctx2.where(field="gender", op=Op.DISTINCT, value=None)
    sql2, _ = ctx2.compile()
    assert "SELECT DISTINCT" in sql2


def test_clickhouse_context_unsupported_op_raises():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    with pytest.raises(ValueError):
        ctx.where(field="gender", op="not-a-real-op", value={"search": "F"})


def test_clickhouse_context_having_unsupported_op_raises():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    with pytest.raises(ValueError):
        ctx.having(field="gender", op="not-a-real-op", value={"search": "F"})


def test_clickhouse_context_count_compile_and_no_columns_selects_star():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    sql, _ = ctx.compile()
    assert "SELECT * FROM employees" in sql
    count_sql, _ = ctx.count_compile()
    assert count_sql.strip().upper().startswith("SELECT COUNT(*)")


def test_clickhouse_context_having_filters_on_aggregated_field():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees", columns=["gender"])
    ctx.where(field="gender", op=Op.GROUP_BY, value=None)
    ctx.having(field="total", op=Op.GT, value={"search": 100})
    sql, params = ctx.compile()
    assert "GROUP BY `gender` HAVING `total` > %(" in sql
    assert 100 in params.values()


def test_clickhouse_context_count_compile_wraps_grouped_query_for_correct_group_count():
    """SELECT count(*) FROM t GROUP BY g would return one row per group, each
    holding that group's row count - not the number of groups. Pagination
    needs the latter, so a grouped/having count wraps as a derived table."""
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees", columns=["gender"])
    ctx.where(field="gender", op=Op.GROUP_BY, value=None)
    ctx.having(field="total", op=Op.GT, value={"search": 100})
    count_sql, count_params = ctx.count_compile()
    assert count_sql.startswith("SELECT count(*) FROM (SELECT 1 FROM employees GROUP BY `gender` HAVING")
    assert 100 in count_params.values()

    # ungrouped: stays the simple direct form, no wrapping needed
    plain_ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    plain_sql, _ = plain_ctx.count_compile()
    assert plain_sql == "SELECT count(*) FROM employees"


def test_clickhouse_context_order_by_raw_expresses_compound_tiebreak():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    ctx.order_by_raw("(emp_no = 1) DESC, gender ASC")
    sql, _ = ctx.compile()
    assert "ORDER BY (emp_no = 1) DESC, gender ASC" in sql


def test_clickhouse_context_add_raw_condition_binds_values_not_identifiers():
    from fastapi_listing.context.clickhouse import quote_identifier

    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    col = quote_identifier("gender")
    ctx.add_raw_condition(f"multiSearchAnyCaseInsensitive({col}, {{needles}})", needles=["m", "f"])
    sql, params = ctx.compile()
    assert "multiSearchAnyCaseInsensitive(`gender`, %(" in sql
    assert ["m", "f"] in params.values()


def test_clickhouse_context_add_raw_condition_having():
    from fastapi_listing.context.clickhouse import quote_identifier

    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    col = quote_identifier("total")
    ctx.add_raw_condition(f"{col} > {{threshold}}", having=True, threshold=100)
    sql, params = ctx.compile()
    assert "HAVING `total` > %(" in sql
    assert 100 in params.values()


def test_having_mixin_routes_canonical_filter_through_having():
    class TotalAboveHaving(generic_filters.HavingMixin, generic_filters.DataGreaterThanFilter):
        pass

    assert TotalAboveHaving.target_clause == "having"

    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    flt = TotalAboveHaving(extra_context={}, field_extract_fn=lambda x: x)
    flt.filter(field="total", value={"search": 100}, context=ctx)
    sql, params = ctx.compile()
    assert "HAVING `total` > %(" in sql
    assert 100 in params.values()


def test_clickhouse_context_native_returns_compiled_sql_and_params():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    ctx.where(field="gender", op=Op.EQ, value={"search": "F"})
    sql, params = ctx.native
    assert "employees" in sql
    assert params == {"__fl_p1": "F"}


def test_clickhouse_context_limit_offset_with_nonzero_offset():
    ctx = ClickHouseQueryContext(client=FakeClickHouseClient(), table="employees")
    ctx.limit_offset(limit=10, offset=20)
    sql, _ = ctx.compile()
    assert "LIMIT 10" in sql
    assert "OFFSET 20" in sql


def test_clickhouse_context_from_raw_sql_wraps_custom_query_untouched():
    """The full-bypass escape hatch: a hand-built query (CTEs, joins, window
    functions, whatever the canonical Op vocabulary can't express) is wrapped
    as a derived table, own params preserved, and canonical where/order/limit
    still layer on top without colliding with the caller's own param names."""
    raw_sql = (
        "WITH ranked AS (SELECT emp_no, channel, "
        "row_number() OVER (PARTITION BY channel ORDER BY emp_no) AS rn "
        "FROM some_table WHERE account_id = %(account_id)s) "
        "SELECT emp_no, channel FROM ranked"
    )
    ctx = ClickHouseQueryContext.from_raw_sql(
        client=FakeClickHouseClient(), sql=raw_sql, params={"account_id": 1001})
    ctx.where(field="channel", op=Op.EQ, value={"search": "organic"})
    ctx.limit_offset(limit=5, offset=0)

    sql, params = ctx.compile()
    assert raw_sql in sql
    assert "account_id" in params and params["account_id"] == 1001
    assert any(k.startswith("__fl_") for k in params if k != "account_id")
    assert "LIMIT 5" in sql

    count_sql, count_params = ctx.count_compile()
    assert raw_sql in count_sql
    assert count_params["account_id"] == 1001


# ---------- CommonFilterImpl deprecation alias ----------

def test_common_filter_impl_alias_warns_on_instantiation():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        generic_filters.CommonFilterImpl(extra_context={})
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


# ---------- PaginationStrategy.postprocess hook ----------

class _UppercasingPaginator(PaginationStrategy):
    def postprocess(self, rows, extra_context):
        return [{"emp_no": r.emp_no, "first_name": r.first_name.upper()} for r in rows]


strategy_factory.register_strategy("uppercasing_paginator_test", _UppercasingPaginator)


def test_postprocess_hook_transforms_rows_before_page_envelope():
    dao = EmployeeDao(read_db=session_factory())
    resp = FastapiListing(dao=dao, fields_to_fetch=["emp_no", "first_name"]).get_response(
        MetaInfo(default_srt_on="emp_no", default_srt_ord="asc",
                paginating_strategy="uppercasing_paginator_test")
    )
    assert [row["first_name"] for row in resp["data"]] == ["SACHIN", "RAHUL", "ANJALI", "PRIYA"]


def test_postprocess_hook_default_is_identity():
    dao = EmployeeDao(read_db=session_factory())
    resp = FastapiListing(dao=dao, fields_to_fetch=["emp_no", "first_name"]).get_response(
        MetaInfo(default_srt_on="emp_no", default_srt_ord="asc")
    )
    assert [row.first_name for row in resp["data"]] == ["Sachin", "Rahul", "Anjali", "Priya"]
