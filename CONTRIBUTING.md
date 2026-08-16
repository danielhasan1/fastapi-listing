# Contributing

## Running the test suite locally

```bash
pip install -e .[test,clickhouse]
```

Most of the suite runs without any external services. Two things need real databases:

- **MySQL** (the `employees` sample DB) - required for the SQLAlchemy-backed HTTP-level tests
  (`tests/test_main.py`, `tests/test_main_v2.py`, `tests/test_fast_listing_compact_version.py`). Without
  it, those tests fail with `ModuleNotFoundError: No module named 'MySQLdb'` or a connection error -
  everything else in the suite still runs and still means something.
- **ClickHouse** - only `tests/test_clickhouse_real_integration.py` needs it, and it **skips
  gracefully** (not a failure) if nothing is reachable. Every other ClickHouse-related test
  (`test_clickhouse_backend.py`, the `Op` coverage in `test_query_context.py`) runs against an
  in-process fake client and needs no real server - the real-integration file exists specifically to
  catch anything a fake client's pattern-matching could miss (real dialect quirks, real parameter
  binding behavior).

Bring both up with:

```bash
docker compose -f docker-compose.dev.yml up -d
docker exec fastapi_listing_mysql bash setup-data   # first run only, loads the sample data
```

Then run everything, including the real-database tests:

```bash
PYTHONPATH=. pytest --cov=fastapi_listing --cov=tests --cov-report=term-missing --cov-fail-under=80
```

Tear down when done: `docker compose -f docker-compose.dev.yml down`.

If you only have one of the two running, that's fine - the suite degrades gracefully either way
(MySQL-dependent tests fail loudly since they're a hard requirement for that HTTP-level path;
ClickHouse's real-server test simply skips).

## CI

`.github/workflows/tests.yml` provisions both automatically (matrixed across Python 3.7-3.11), so
neither is optional there - a PR is expected to pass with both available.
