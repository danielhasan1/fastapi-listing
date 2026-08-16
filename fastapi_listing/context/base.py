"""Backend-agnostic query context.

A QueryContext is the object threaded through Filter.filter() / Sorter.sort() /
QueryStrategy.get_query() / Paginator.paginate() in place of a raw SQLAlchemy
Query. Each backend (SQLAlchemy, ClickHouse, ...) implements this contract once;
every canonical Filter subclass and the default Sorter/Paginator/QueryStrategy
work unchanged against any implementation.

`native` is always available as an escape hatch for backend-specific needs the
canonical Op vocabulary doesn't cover (joins, eager loading, aggregates, ...).
"""

from abc import ABC, abstractmethod
from typing import Any, Sequence

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi_listing.ops import Op

__all__ = ["QueryContext"]


class QueryContext(ABC):

    @property
    @abstractmethod
    def native(self) -> Any:
        """Escape hatch to the underlying backend object (a SQLAlchemy Query,
        a (sql, params) tuple, ...) for logic the canonical Op vocabulary
        can't express."""

    @abstractmethod
    def where(self, *, field: Any, op: Op, value: Any) -> "QueryContext":
        """Apply one canonical operation (see fastapi_listing.ops.Op). This is
        the single dispatch point for every Filter subclass, including the
        value-less GROUP_BY/DISTINCT operations."""

    @abstractmethod
    def having(self, *, field: Any, op: Op, value: Any) -> "QueryContext":
        """Same Op vocabulary as where(), but lands in a HAVING clause instead
        of WHERE - for filtering on an aggregated field (e.g. `SUM(x) > 100`)
        after a GROUP_BY, which WHERE cannot express. A CanonicalFilter opts
        into this by setting `target_clause = "having"`."""

    @abstractmethod
    def order_by(self, *, field: Any, direction: Literal["asc", "dsc"]) -> "QueryContext":
        pass

    @abstractmethod
    def limit_offset(self, *, limit: int, offset: int) -> "QueryContext":
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def fetch(self) -> Sequence:
        pass
