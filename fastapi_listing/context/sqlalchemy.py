"""SQLAlchemy QueryContext adapter.

Thin pass-through wrapping a SQLAlchemy Query. `where()` dispatches each
canonical Op to the exact fluent-API call the old per-backend filter classes
used to make directly - moved here verbatim, not rewritten.
"""

from typing import Any, Sequence

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi_listing.context.base import QueryContext
from fastapi_listing.ops import Op

__all__ = ["SqlAlchemyQueryContext"]


class SqlAlchemyQueryContext(QueryContext):

    def __init__(self, query):
        self._query = query

    @property
    def native(self):
        return self._query

    def with_native(self, query) -> "SqlAlchemyQueryContext":
        """Rewrap a Query a caller mutated directly via `.native` (e.g. after
        a custom .join()/.options() call the canonical Op vocabulary can't
        express)."""
        self._query = query
        return self

    @staticmethod
    def _condition(*, field, op: Op, value):
        """Build the boolean expression for a comparison Op - shared by
        where() and having(), since a HAVING clause is the same Op vocabulary
        applied to an aggregated field rather than a raw column."""
        if op is Op.EQ:
            return field == value.get("search")
        elif op is Op.NEQ:
            return field != value.get("search")
        elif op is Op.IN:
            return field.in_(value.get("list"))
        elif op is Op.RANGE:
            return field.between(value.get("start"), value.get("end"))
        elif op is Op.LIKE:
            return field.like(value.get("search"))
        elif op is Op.STARTS_WITH:
            return field.startswith(value.get("search"))
        elif op is Op.ENDS_WITH:
            return field.endswith(value.get("search"))
        elif op is Op.CONTAINS:
            return field.contains(value.get("search"))
        elif op is Op.GT:
            return field > value.get("search")
        elif op is Op.GTE:
            return field >= value.get("search")
        elif op is Op.LT:
            return field < value.get("search")
        elif op is Op.LTE:
            return field <= value.get("search")
        elif op is Op.NOT_NULL:
            return field.is_not(None)
        elif op is Op.IS_NULL:
            return field.is_(None)
        raise ValueError(f"Unsupported comparison op: {op!r}")

    def where(self, *, field, op: Op, value) -> "SqlAlchemyQueryContext":
        if op is Op.GROUP_BY:
            self._query = self._query.group_by(field)
        elif op is Op.DISTINCT:
            self._query = self._query.distinct(field)
        elif op in (Op.EQ, Op.NEQ, Op.IN, Op.RANGE, Op.LIKE, Op.STARTS_WITH, Op.ENDS_WITH, Op.CONTAINS,
                    Op.GT, Op.GTE, Op.LT, Op.LTE, Op.NOT_NULL, Op.IS_NULL):
            self._query = self._query.filter(self._condition(field=field, op=op, value=value))
        else:
            raise ValueError(f"Unsupported op for SqlAlchemyQueryContext.where(): {op!r}")
        return self

    def having(self, *, field, op: Op, value) -> "SqlAlchemyQueryContext":
        self._query = self._query.having(self._condition(field=field, op=op, value=value))
        return self

    def order_by(self, *, field, direction: Literal["asc", "dsc"]) -> "SqlAlchemyQueryContext":
        self._query = self._query.order_by(field.asc() if direction == "asc" else field.desc())
        return self

    def limit_offset(self, *, limit: int, offset: int) -> "SqlAlchemyQueryContext":
        self._query = self._query.limit(limit).offset(offset)
        return self

    def count(self) -> int:
        return self._query.count()

    def fetch(self) -> Sequence:
        return self._query.all()
