# fastapi-listing — working notes for Claude Code

This file persists the architectural decisions, conventions, and hard-won lessons from the 0.4.0
backend-agnostic rework so a future session (after context compaction, or a brand new conversation)
doesn't have to re-derive them from scratch.

## What 0.4.0 actually did

The library's Filter/Sorter/Paginator/QueryStrategy contracts were pluggable in theory but every
default implementation talked to a raw SQLAlchemy `Query` directly, and four modules imported
SQLAlchemy unconditionally at load time (so the library couldn't even be imported without it). 0.4.0
introduced `QueryContext` (`fastapi_listing/context/`) as the real seam, with `SqlAlchemyQueryContext`
as the default backend and `ClickHouseQueryContext` as a reference non-ORM backend proving the
abstraction actually generalizes. See `CHANGELOG.md` for the full breaking-change/migration details -
don't duplicate that here, it's kept current.

## The core design rule (keep applying it)

**Structural, request-scoped query shape belongs in the DAO/QueryStrategy, resolved once per request
from parameters. Generic listing concerns (comparisons on an exposed column, sort, pagination) belong
in canonical `Filter`/`Op` classes.** This line gets litigated on every new feature - a filter that
needs to reach inside a pre-aggregated CTE, or a sort that needs a business-rule tiebreak, is not
something canonical filters should be forced to express. Reach for the narrowest escape hatch instead:

- `context.native` (SQLAlchemy) / `ClickHouseQueryContext.from_raw_sql()` - full bypass, hand-build the
  whole query (CTEs, joins, window functions, a table function as the source).
- `HavingMixin` - canonical `Op`, routed to `HAVING` instead of `WHERE`, for filtering on an aggregated
  field after a `GROUP BY`.
- `order_by_raw()` - a compound ordering rule (a tiebreak column, multiple sort keys) that a single
  `field, direction` pair can't express.
- `add_raw_condition()` - a single filter needing a backend-specific SQL builtin (e.g.
  `multiSearchAnyCaseInsensitive`) with no canonical `Op` equivalent. Values still bind through the
  driver's real parameter binding; only the resolved field/column identifier is spliced in directly.

None of this is speculative - `from_raw_sql`/`HavingMixin`/`order_by_raw`/`add_raw_condition` were all
validated against a **real** ClickHouse server (not just the fake-client unit tests) during this work.
`ClickHouseQueryContext.count_compile()` wraps grouped queries as a derived table when counting
(`GROUP BY` directly would return one count *per group*, not the total) - this was a real bug, caught
and fixed, confirmed correct against a real server too.

## Known warts (real, pre-existing, deliberately not fixed - don't rediscover these as new bugs)

- `filter_factory` (`fastapi_listing/factory/filter.py`) registers by **field path**, not by alias. Two
  different operators on the *same* column (e.g. an `eq` and a `gt` filter both resolving to
  `indexed_pages`) collide as duplicate registrations. Workaround already used in the codebase's own
  tests (`tests/service_setup.py`'s `"DeptEmp1.to_date"`/`"DeptEmp2.to_date"`): give each a distinct
  decoy namespace prefix before the last dot - `extract_field()` only ever reads the segment after the
  final `.`, so `"my_decoy_ns.indexed_pages"` still resolves to the `indexed_pages` attribute.
- `dao_factory.create(key)` raises a bare `ValueError` if `key` was never registered, and only raises
  `MissingSessionError` (which `ListingService.__init__` catches to fall back to manual construction)
  if the key *is* registered but no session is bound. A DAO must be `dao_factory.register_dao(...)`'d
  even if you never intend to use the factory-bound-session path, or the fallback in
  `ListingService.__init__` never triggers correctly.
- `middlewares.py`'s `_session`/`_replica_session` are shared, module-level `ContextVar`s. The
  `manager()` cleanup logic used to infer "did this call set a token" from the ContextVar's *current*
  value - which could be a leftover from an earlier, unrelated call (especially with
  `implicit_close=False`, which deliberately never resets). Fixed by tracking token assignment locally
  per call instead. If you touch `manager()` again, don't reintroduce that inference.
- There is no ClickHouse equivalent of `DaoSessionBinderMiddleware` - deliberate, not an oversight. See
  "Don't build speculative infrastructure" below.
- `interface/client_site_params_adapter.py` is dead code - grepped, referenced nowhere in the package.
  Left alone (deletion is a separate, smaller decision), marked `# pragma: no cover` along with
  `interface/listing_meta_info.py`'s `Protocol` (structural type stubs, not real coverage gaps).

## Don't build speculative infrastructure for hypothetical backends

Explicitly decided: no auto-configuring connection-binding middleware for ClickHouse (or any future
backend) inside the library itself. There are too many ORMs/drivers/connection strategies to support
out of the box, and building one for ClickHouse specifically (when nobody's asked for it yet) would be
solving a problem nobody has. The pattern - construct your own client, pass it to the DAO directly, or
write your own thin `ContextVar`-based binder mirroring `middlewares.py` if you want per-request
lifecycle - is the intended, documented answer. Don't second-guess this into "should we add it" again
without a concrete need driving it.

## Safety rule - do not relax this one

An earlier version of this work included an `examples/` directory demonstrating a ClickHouse
conversion, built by directly reading a real production codebase (a specific employer's internal
system) for structural reference. Even after renaming identifiers, it was still a recognizable
derivative (matching filter-op vocabulary, exact metric-calculation shape, real ClickHouse builtin
usage patterns) of that real system - "reskinning" wasn't sufficient. It was removed entirely, and a
real account ID that had leaked into a *committed test* (not just the example) was scrubbed before
ever being pushed. **Never build examples, tests, or documentation by structurally mirroring a real
company's actual production code, even disguised.** If a real-world case study is ever wanted again, it
must be invented from a made-up domain, not derived from having read someone else's real system.

## Testing philosophy applied throughout this work

- Cross-check "missing coverage" against what the *real* CI (real MySQL, matrix across Python
  3.7-3.11) actually shows before writing a test - a lot of apparent gaps in a sandbox without MySQL
  access are illusory (the MySQL-dependent tests fail on `ModuleNotFoundError: MySQLdb` before ever
  reaching the code in question, not a real gap). Chase the ones that are still missing in the real CI
  logs, or that are testable without a database at all (pure Python logic - validation branches,
  factory registries, ContextVar plumbing).
- Some gaps are genuinely not worth chasing: version-dependent fallback branches (`typing.Literal`
  pre-3.8, SQLAlchemy-absent, pydantic v1-vs-v2) only ever take one branch per environment/interpreter
  - don't fabricate multi-environment test matrices to "fix" these; they average out across the real CI
  matrix already.
- Prefer a real, throwaway local ClickHouse instance (`clickhouse local`/`clickhouse server`, the
  official all-in-one binary) over only trusting fake-client unit tests when validating anything
  ClickHouse-dialect-specific. Fakes prove internal consistency; a real server proves the SQL is
  actually valid.
- When adding tests, don't pad for a coverage number - every test added during this work was tied to a
  specific, real, previously-untested branch, cross-referenced against the real CI's line-by-line
  "Missing" column first.

## Git/release conventions for this repo specifically

- `~/dev/personal/` has a conditional gitconfig include (`~/.gitconfig-personal`) - commits here use
  the `danielhasan1`/`dh813030@gmail.com` identity, SSH remote, and **no** `Co-Authored-By` or
  `Change-Id` trailers (the latter was a leftover Gerrit `commit-msg` hook from a work identity,
  disabled here via `core.hooksPath = .git/hooks`).
- No fixed rule on squash-vs-new-commit: default judgment call based on whether the new change is part
  of the same logical unit of work already on the branch, but always ask/confirm before amending +
  force-pushing something already on the remote.
- Breaking changes on a pre-1.0 library are spec-compliant to ship as a MINOR version bump (semver
  explicitly allows this for `0.x`), not necessarily a major bump - already applied (0.3.4 -> 0.4.0).
- `setup.py`'s `Development Status` classifier should reflect actual real-world validation, not just
  "the code passed CI." A breaking rework with a brand-new, not-yet-battle-tested backend shipping
  under `"5 - Production/Stable"` overstates it - step down to `"4 - Beta"` for a release like this,
  move back up once the new parts have real usage behind them.
- Standard practice for OSS releases: you cannot and should not try to test every possible downstream
  usage before shipping - that's what pre-releases, a clear CHANGELOG/migration guide, and loud
  actionable errors (`FastapiListingMigrationError`) are for. What you *can and must* verify yourself is
  your own direct usage/customizations, since nothing else does that for you.
