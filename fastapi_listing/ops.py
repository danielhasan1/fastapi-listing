"""Canonical, backend-agnostic filter operations.

Every backend's QueryContext interprets the same Op values in whatever way makes
sense for it (a SQLAlchemy `.filter()` chain, a raw SQL WHERE fragment, a Mongo
filter dict, ...). Filter classes in `fastapi_listing.filters` only ever declare
*which* Op they represent - they never touch a specific backend's syntax.
"""

from enum import Enum

__all__ = ["Op"]


class Op(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    IN = "in"
    RANGE = "range"
    LIKE = "like"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IS_NULL = "is_null"
    NOT_NULL = "not_null"
    GROUP_BY = "group_by"
    DISTINCT = "distinct"
