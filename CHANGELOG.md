# Changelog

## 0.4.0

**Breaking change** for anyone who wrote a custom `Filter`, `Sorter`, `QueryStrategy`, or `PaginationStrategy`
subclass. **Not** breaking for the plain README flow (`GenericDao` + `generic_filters` + default strategies) -
that continues to work unchanged.

### Why

fastapi-listing's Filter/Sorter/Paginator/QueryStrategy contracts were pluggable in theory, but every shipped
default implementation talked to a raw SQLAlchemy `Query` directly, and four modules imported SQLAlchemy
unconditionally at module load time - so the library couldn't even be imported without SQLAlchemy installed,
let alone actually used with a different backend. This release makes the contract genuinely backend-agnostic
and ships a ClickHouse reference implementation (raw parameterized SQL, no ORM) as proof.

### What changed

- A raw `query` object is replaced everywhere by a `QueryContext` (`fastapi_listing.context.QueryContext`):
  `Filter.filter(..., context=...)`, `Sorter.sort(..., context=...)`, `Paginator.paginate(context, ...)`,
  `QueryStrategy.get_query(...) -> QueryContext`. For SQLAlchemy this is `SqlAlchemyQueryContext`, a thin
  wrapper - reach `context.native` for the underlying `Query` when you need something the canonical filter
  vocabulary doesn't cover (joins, eager loading, aggregates), then hand it back via `context.with_native(...)`.
- `generic_filters.CommonFilterImpl` is renamed `CanonicalFilter` (kept as a deprecated alias, raises
  `DeprecationWarning` on instantiation, will be removed in a future release). The 14 built-in filter classes
  (`EqualityFilter`, `InDataFilter`, ...) now each just declare a canonical `Op` (`fastapi_listing.ops.Op`) and
  work unchanged against *any* backend - no per-backend filter subclassing needed.
- Added `PaginationStrategy.postprocess(rows, extra_context)` - identity by default, a dedicated seam for
  post-fetch business logic (bucket-filling, tie-break re-sorting, export-shape reshaping) that previously had
  no governed home.
- `import fastapi_listing` no longer requires SQLAlchemy to be installed (it's now correctly optional, matching
  what `setup.py` already claimed). Neither SQLAlchemy nor the new `clickhouse-driver` extra are in
  `install_requires` - both are opt-in (`pip install fastapi-listing[clickhouse]` for the ClickHouse backend).
- Added a reference non-ORM backend: `fastapi_listing.dao.ClickHouseDao` + `fastapi_listing.context.clickhouse.ClickHouseQueryContext`,
  built on `clickhouse-driver` with real server-side parameter binding (no value is ever string-formatted into
  SQL text).
- Loud, actionable failures instead of a bare traceback if you upgrade without migrating: a custom
  `Filter`/`Sorter` still using the old `query=` parameter name, or a custom `QueryStrategy` returning a raw
  `Query` instead of a `QueryContext`, now raises `FastapiListingMigrationError` with a specific fix, not a
  generic `TypeError`/`AttributeError`.
- `loader.py`'s DAO type check now validates against `DaoAbstract` (the actual abstract contract) instead of
  hardcoding `GenericDao`, so non-SQLAlchemy DAOs (like `ClickHouseDao`) register the same way SQLAlchemy ones
  always have. Error message changed accordingly: `"Invalid Dao Type! Should Be type of DaoAbstract"`.
- Added `QueryContext.having()` (and `ClickHouseQueryContext.from_raw_sql()` for the full bypass - hand-build a
  query with CTEs/joins/window functions/whatever, still get back a `QueryContext` canonical filters/sort/
  pagination can layer on top of). Filter on an aggregated field after a `GROUP_BY` via `HavingMixin`, e.g.
  `class TotalAbove(HavingMixin, DataGreaterThanFilter): pass` - `WHERE` can't express that, `HAVING` can, same
  `Op` vocabulary. Along the way, fixed a latent bug in `ClickHouseQueryContext.count_compile()`: counting a
  `GROUP BY` query directly returns one count *per group*, not the total number of groups: it now wraps as a
  derived table when grouped/having, matching what SQLAlchemy's `Query.count()` already did automatically.

### Migration

If you only use the built-in `generic_filters`, the default strategies, and `GenericDao` subclasses - **you
don't need to do anything.**

If you wrote a custom subclass:

| Was | Now |
|---|---|
| `def filter(self, *, field=None, value=None, query=None)` | `def filter(self, *, field=None, value=None, context=None)` |
| `query.filter(...)` inside a custom filter | `context.native.filter(...)`, then `context = context.with_native(new_query)` |
| `def sort(self, *, query=None, ...)` | `def sort(self, *, context=None, ...)` |
| `def get_query(...) -> Query: return dao.some_method()` | `return SqlAlchemyQueryContext(dao.some_method())` |
| `CommonFilterImpl` | `CanonicalFilter` (alias still works, warns) |

See `docs/query.rst` and `docs/filters.rst` for full examples.
