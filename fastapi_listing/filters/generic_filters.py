__all__ = [
    "CanonicalFilter",
    "CommonFilterImpl",
    "HavingMixin",
    "EqualityFilter",
    "InEqualityFilter",
    "InDataFilter",
    "BetweenUnixMilliSecDateFilter",
    "StringStartsWithFilter",
    "StringEndsWithFilter",
    "StringContainsFilter",
    "StringLikeFilter",
    "DataGreaterThanFilter",
    "DataGreaterThanEqualToFilter",
    "DataLessThanFilter",
    "DataLessThanEqualToFilter",
    "DataGropByElementFilter",
    "DataDistinctByElementFilter",
    "HasFieldValue",
    "MySqlNativeDateFormateRangeFilter",
]

from abc import ABCMeta
from typing import Callable, ClassVar, Optional
from datetime import datetime
from warnings import warn

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi import Request

from fastapi_listing.abstracts import FilterAbstract
from fastapi_listing.context import QueryContext
from fastapi_listing.ops import Op


class CanonicalFilter(FilterAbstract):
    """
    Declares a canonical Op (see fastapi_listing.ops.Op) and hands off to
    whatever QueryContext the DAO's backend supplies. Backend-specific syntax
    (SQLAlchemy `.filter()` chains, ClickHouse WHERE fragments, ...) lives
    entirely inside the QueryContext implementation - this class and its
    subclasses never touch it, which is what lets the same Filter subclass
    work unchanged against any backend.
    """

    op: ClassVar[Op]
    target_clause: ClassVar[Literal["where", "having"]] = "where"
    """Set to "having" (e.g. via the HavingMixin below) to filter on an
    aggregated field (SUM(x) > 100, ...) after a GROUP_BY - WHERE can't
    express that, HAVING can, using the exact same Op vocabulary."""

    def __init__(self, dao=None, request: Optional[Request] = None, *, extra_context: dict,
                 field_extract_fn: Callable[[str], object] = None):
        # field_extract_fn ex: lambda x: getattr(Model, x)
        self.dao = dao
        self.request = request
        self.extra_context = extra_context
        self.custom_field_extractor = field_extract_fn

    def extract_field(self, field: str):
        field = field.split(".")[-1]
        if self.custom_field_extractor:
            return self.custom_field_extractor(field)
        return getattr(self.dao.model, field)

    def coerce(self, value: dict) -> dict:
        """Override to adapt a raw client-supplied value (unit conversion,
        epoch-ms -> datetime, etc.) before it reaches the QueryContext."""
        return value

    def filter(self, *, field: str = None, value: dict = None,
               context: QueryContext = None) -> QueryContext:
        if value is None and self.op not in (Op.GROUP_BY, Op.DISTINCT):
            return context
        dispatch = context.having if self.target_clause == "having" else context.where
        return dispatch(field=self.extract_field(field), op=self.op, value=self.coerce(value))


class HavingMixin:
    """Mix into any CanonicalFilter op-subclass to route it through HAVING
    instead of WHERE, e.g.:

        class TotalConversionsAbove(HavingMixin, DataGreaterThanFilter):
            pass
    """
    target_clause = "having"


class _CommonFilterImplMeta(ABCMeta):
    def __call__(cls, *args, **kwargs):
        warn("CommonFilterImpl is deprecated, use CanonicalFilter instead.",
             DeprecationWarning, stacklevel=2)
        return super().__call__(*args, **kwargs)


class CommonFilterImpl(CanonicalFilter, metaclass=_CommonFilterImplMeta):
    """Deprecated alias for CanonicalFilter, kept for one release."""


class EqualityFilter(CanonicalFilter):
    op = Op.EQ


class InEqualityFilter(CanonicalFilter):
    op = Op.NEQ


class InDataFilter(CanonicalFilter):
    op = Op.IN


class BetweenUnixMilliSecDateFilter(CanonicalFilter):
    op = Op.RANGE

    def coerce(self, value: dict) -> dict:
        return {
            "start": datetime.fromtimestamp(int(value.get('start')) / 1000),
            "end": datetime.fromtimestamp(int(value.get('end')) / 1000),
        }


class StringStartsWithFilter(CanonicalFilter):
    op = Op.STARTS_WITH


class StringEndsWithFilter(CanonicalFilter):
    op = Op.ENDS_WITH


class StringContainsFilter(CanonicalFilter):
    op = Op.CONTAINS


class StringLikeFilter(CanonicalFilter):
    op = Op.LIKE


class DataGreaterThanFilter(CanonicalFilter):
    op = Op.GT


class DataGreaterThanEqualToFilter(CanonicalFilter):
    op = Op.GTE


class DataLessThanFilter(CanonicalFilter):
    op = Op.LT


class DataLessThanEqualToFilter(CanonicalFilter):
    op = Op.LTE


class DataGropByElementFilter(CanonicalFilter):
    op = Op.GROUP_BY


class DataDistinctByElementFilter(CanonicalFilter):
    op = Op.DISTINCT


class HasFieldValue(CanonicalFilter):
    # op is resolved dynamically from the value flag, so this overrides
    # filter() entirely rather than declaring a fixed canonical op.
    op = Op.NOT_NULL

    def filter(self, *, field: str = None, value: dict = None, context: QueryContext = None) -> QueryContext:
        op = Op.NOT_NULL if value.get("search") else Op.IS_NULL
        return context.where(field=self.extract_field(field), op=op, value=None)


class MySqlNativeDateFormateRangeFilter(CanonicalFilter):
    op = Op.RANGE
