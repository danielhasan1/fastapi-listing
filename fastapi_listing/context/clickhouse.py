"""ClickHouse QueryContext - the proof-of-concept non-ORM backend.

Owns its own WHERE/ORDER BY/GROUP BY/LIMIT fragment accumulation and compiles a
single parameterized SQL statement, executed via `clickhouse-driver`.

Every value flows through the driver's own parameter binding (`%(name)s`
placeholders resolved by `Client.execute(sql, params)`); nothing is ever
string-formatted into the SQL text. Column/field names can't be parameterized
by any SQL driver, but by the time a field reaches `where()`/`order_by()` it has
already been resolved via `getattr(dao.model, field)` upstream (in
CanonicalFilter.extract_field / SortingOrderStrategy.validate_srt_field) against
the DAO's declared model attributes - an unregistered field never reaches here,
it raises AttributeError before this point. That resolution step is this
backend's allowlist, mirroring a hand-written FIELD_COLUMNS mapping.
"""

from typing import Any, Sequence

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi_listing.context.base import QueryContext
from fastapi_listing.ops import Op

__all__ = ["ClickHouseQueryContext", "quote_identifier"]


def _quote_identifier(name: str) -> str:
    return f"`{name}`"


# Public name for use from a custom Filter's add_raw_condition() call, where
# you need to quote a resolved field/column identifier yourself.
quote_identifier = _quote_identifier


class ClickHouseQueryContext(QueryContext):

    def __init__(self, *, client, table: str, columns=None, params=None):
        self._client = client
        self._table = table
        self._columns = list(columns) if columns else None
        self._wheres = []
        self._havings = []
        self._params = dict(params) if params else {}
        self._param_seq = 0
        self._order_by = None
        self._group_by = None
        self._distinct = False
        self._limit = None
        self._offset = None

    @classmethod
    def from_raw_sql(cls, *, client, sql: str, params: dict = None, columns=None) -> "ClickHouseQueryContext":
        """Full bypass for queries the canonical Op vocabulary can't express -
        CTEs, joins, window functions, a runtime-sized UNION ALL, a table
        function as the source, ... Build the whole statement yourself (same
        query-template functions you'd already be writing), hand it here, and
        you still get a QueryContext that plugs into the rest of the pipeline:
        `where()`/`order_by()`/`limit_offset()` wrap it as a derived table, so
        canonical filters/sort/pagination can still layer on top if you want
        them to - or leave filter_mapper empty and let the raw SQL stand as-is.
        `params` are your own already-bound parameter names/values; they are
        merged in untouched (auto-generated bind keys use a distinct '__fl_'
        prefix so they never collide with yours).
        """
        return cls(client=client, table=f"({sql}) AS __fl_raw", columns=columns, params=params)

    @property
    def native(self):
        return self.compile()

    def _bind(self, value) -> str:
        self._param_seq += 1
        key = f"__fl_p{self._param_seq}"
        self._params[key] = value
        return key

    def _condition_sql(self, *, field, op: Op, value) -> str:
        """Build the SQL fragment for a comparison Op, binding any values along
        the way - shared by where() and having(), since a HAVING clause is the
        same Op vocabulary applied to an aggregated field rather than a raw
        column."""
        col = _quote_identifier(field)
        if op is Op.EQ:
            return f"{col} = %({self._bind(value.get('search'))})s"
        elif op is Op.NEQ:
            return f"{col} != %({self._bind(value.get('search'))})s"
        elif op is Op.IN:
            return f"{col} IN %({self._bind(tuple(value.get('list') or []))})s"
        elif op is Op.RANGE:
            start_key = self._bind(value.get("start"))
            end_key = self._bind(value.get("end"))
            return f"{col} BETWEEN %({start_key})s AND %({end_key})s"
        elif op is Op.LIKE:
            return f"{col} LIKE %({self._bind(value.get('search'))})s"
        elif op is Op.STARTS_WITH:
            search = value.get("search")
            return f"{col} LIKE %({self._bind(f'{search}%')})s"
        elif op is Op.ENDS_WITH:
            search = value.get("search")
            return f"{col} LIKE %({self._bind(f'%{search}')})s"
        elif op is Op.CONTAINS:
            search = value.get("search")
            return f"{col} LIKE %({self._bind(f'%{search}%')})s"
        elif op is Op.GT:
            return f"{col} > %({self._bind(value.get('search'))})s"
        elif op is Op.GTE:
            return f"{col} >= %({self._bind(value.get('search'))})s"
        elif op is Op.LT:
            return f"{col} < %({self._bind(value.get('search'))})s"
        elif op is Op.LTE:
            return f"{col} <= %({self._bind(value.get('search'))})s"
        elif op is Op.NOT_NULL:
            return f"{col} IS NOT NULL"
        elif op is Op.IS_NULL:
            return f"{col} IS NULL"
        raise ValueError(f"Unsupported comparison op: {op!r}")

    def where(self, *, field, op: Op, value) -> "ClickHouseQueryContext":
        if op is Op.GROUP_BY:
            self._group_by = _quote_identifier(field)
        elif op is Op.DISTINCT:
            self._distinct = True
        elif op in (Op.EQ, Op.NEQ, Op.IN, Op.RANGE, Op.LIKE, Op.STARTS_WITH, Op.ENDS_WITH, Op.CONTAINS,
                    Op.GT, Op.GTE, Op.LT, Op.LTE, Op.NOT_NULL, Op.IS_NULL):
            self._wheres.append(self._condition_sql(field=field, op=op, value=value))
        else:
            raise ValueError(f"Unsupported op for ClickHouseQueryContext.where(): {op!r}")
        return self

    def having(self, *, field, op: Op, value) -> "ClickHouseQueryContext":
        self._havings.append(self._condition_sql(field=field, op=op, value=value))
        return self

    def add_raw_condition(self, sql_template: str, *, having: bool = False, **values) -> "ClickHouseQueryContext":
        """Per-filter escape hatch for a WHERE/HAVING condition using
        ClickHouse-specific syntax the canonical Op vocabulary doesn't cover
        (a builtin function like multiSearchAnyCaseInsensitive, an array
        literal, ...) - the ClickHouse-side equivalent of reaching into
        SqlAlchemyQueryContext.native from inside a custom Filter.

        `sql_template` uses `{name}` placeholders for each of **values; every
        value is still bound through the driver's own parameter binding, never
        string-formatted into the SQL text directly. A resolved field/column
        name is an identifier, not a value - quote and splice it into the
        template yourself (matching how every other op already does it here),
        don't pass it through **values. Example:

            col = _quote_identifier(field)
            context.add_raw_condition(
                f"multiSearchAnyCaseInsensitive({col}, {{needles}})",
                needles=list_of_substrings,
            )
        """
        bound = {name: f"%({self._bind(value)})s" for name, value in values.items()}
        condition = sql_template.format(**bound)
        (self._havings if having else self._wheres).append(condition)
        return self

    def order_by(self, *, field, direction: Literal["asc", "dsc"]) -> "ClickHouseQueryContext":
        self._order_by = f"{_quote_identifier(field)} {'ASC' if direction == 'asc' else 'DESC'}"
        return self

    def order_by_raw(self, expression: str) -> "ClickHouseQueryContext":
        """Escape hatch for ordering the canonical order_by(field, direction)
        can't express - a compound tiebreak expression, multiple sort keys,
        `(x = 1) DESC, y ASC`, ... Same philosophy as from_raw_sql: drop to
        raw SQL only where the canonical vocabulary genuinely doesn't reach."""
        self._order_by = expression
        return self

    def limit_offset(self, *, limit: int, offset: int) -> "ClickHouseQueryContext":
        self._limit = limit
        self._offset = offset
        return self

    def _where_sql(self) -> str:
        return f" WHERE {' AND '.join(self._wheres)}" if self._wheres else ""

    def _having_sql(self) -> str:
        return f" HAVING {' AND '.join(self._havings)}" if self._havings else ""

    def _select_columns_sql(self) -> str:
        if not self._columns:
            return "*"
        return ", ".join(_quote_identifier(c) for c in self._columns)

    def _grouped_body_sql(self, select_list: str) -> str:
        """The shared FROM ... WHERE ... GROUP BY ... HAVING ... body, used by
        both compile() (selecting real columns) and count_compile() (selecting
        a constant, for wrapping)."""
        sql = f"SELECT {select_list} FROM {self._table}"
        sql += self._where_sql()
        if self._group_by:
            sql += f" GROUP BY {self._group_by}"
        sql += self._having_sql()
        return sql

    def compile(self):
        """Return (sql, params) for the row-fetching statement, without executing it."""
        select_list = f"{'DISTINCT ' if self._distinct else ''}{self._select_columns_sql()}"
        sql = self._grouped_body_sql(select_list)
        if self._order_by:
            sql += f" ORDER BY {self._order_by}"
        if self._limit is not None:
            sql += f" LIMIT {int(self._limit)}"
            if self._offset:
                sql += f" OFFSET {int(self._offset)}"
        return sql, dict(self._params)

    def count_compile(self):
        """Return (sql, params) for the count statement, without executing it.

        Plain (no GROUP BY/HAVING): a direct `SELECT count(*) FROM ... WHERE ...`.
        Grouped/aggregated: counting rows of a GROUP BY query directly would
        return one count *per group*, not the total number of groups - so the
        grouped body is wrapped as a derived table and counted from outside,
        matching what SQLAlchemy's Query.count() already does automatically.
        """
        if self._group_by or self._havings:
            inner = self._grouped_body_sql("1")
            return f"SELECT count(*) FROM ({inner})", dict(self._params)
        sql = f"SELECT count(*) FROM {self._table}{self._where_sql()}"
        return sql, dict(self._params)

    def count(self) -> int:
        sql, params = self.count_compile()
        rows = self._client.execute(sql, params)
        return rows[0][0]

    def fetch(self) -> Sequence:
        sql, params = self.compile()
        rows, columns_with_types = self._client.execute(sql, params, with_column_types=True)
        column_names = [c[0] for c in columns_with_types]
        return [dict(zip(column_names, row)) for row in rows]
