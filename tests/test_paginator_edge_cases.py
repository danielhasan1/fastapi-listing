"""PaginationStrategy's validation/pagination-math branches are plain Python
logic operating on a QueryContext through its public count()/fetch()/
limit_offset() interface - none of it needs a real database, so a minimal fake
context is enough to exercise every branch directly.
"""

import pytest

from fastapi_listing.errors import ListingPaginatorError
from fastapi_listing.paginator import PaginationStrategy


class _FakeContext:
    """Just enough of QueryContext for PaginationStrategy to drive - no real
    backend needed since these are pure pagination-math/validation tests."""

    def __init__(self, rows):
        self._rows = list(rows)
        self._limit = None
        self._offset = None

    def limit_offset(self, *, limit, offset):
        self._limit = limit
        self._offset = offset
        return self

    def count(self):
        return len(self._rows)

    def fetch(self):
        if self._limit is None:
            return self._rows
        return self._rows[self._offset:self._offset + self._limit]


@pytest.mark.parametrize("page_num,page_size", [
    (1.5, 1), (1, 1.5), ("x", 1), (1, "x"), (None, 1), (1, None),
])
def test_validate_params_rejects_non_integers(page_num, page_size):
    strategy = PaginationStrategy()
    with pytest.raises(ListingPaginatorError, match="not valid integers"):
        strategy.validate_params(page_num, page_size)


@pytest.mark.parametrize("page_num,page_size", [(0, 1), (1, 0), (-1, 5), (1, -1)])
def test_validate_params_rejects_less_than_one(page_num, page_size):
    strategy = PaginationStrategy()
    with pytest.raises(ListingPaginatorError, match="less than 1"):
        strategy.validate_params(page_num, page_size)


def test_validate_params_accepts_whole_number_floats():
    strategy = PaginationStrategy()
    strategy.validate_params(2.0, 10.0)  # should not raise


def test_paginate_falls_back_to_page_1_size_10_on_invalid_params():
    strategy = PaginationStrategy()
    context = _FakeContext(range(25))
    page = strategy.paginate(context, {"page": "not-a-number", "pageSize": 5}, {})
    assert page["currentPageNumber"] == 1
    assert page["currentPageSize"] == 10


def test_is_next_page_exists_with_count_query():
    strategy = PaginationStrategy()
    strategy.set_count(25)
    strategy.set_page_num(1)
    strategy.set_page_size(10)
    assert strategy.is_next_page_exists() is True
    strategy.set_page_num(3)
    assert strategy.is_next_page_exists() is False


def test_is_next_page_exists_without_count_query():
    strategy = PaginationStrategy(fire_count_qry=False)
    strategy.set_page_size(10)
    strategy.set_count(11)
    assert strategy.is_next_page_exists() is True
    strategy.set_count(10)
    assert strategy.is_next_page_exists() is False


def test_page_without_count_trims_the_lookahead_row_when_has_next():
    strategy = PaginationStrategy(fire_count_qry=False)
    context = _FakeContext(range(11))  # page_size + 1 lookahead trick
    page = strategy.paginate(context, {"page": 1, "pageSize": 10}, {})
    assert page["hasNext"] is True
    assert len(page["data"]) == 10


def test_page_without_count_returns_all_rows_when_no_next_page():
    strategy = PaginationStrategy(fire_count_qry=False)
    context = _FakeContext(range(5))
    page = strategy.paginate(context, {"page": 1, "pageSize": 10}, {})
    assert page["hasNext"] is False
    assert len(page["data"]) == 5


def test_paginate_with_count_query_returns_full_page_envelope():
    strategy = PaginationStrategy()
    context = _FakeContext(range(25))
    page = strategy.paginate(context, {"page": 2, "pageSize": 10}, {})
    assert page["totalCount"] == 25
    assert page["currentPageNumber"] == 2
    assert page["currentPageSize"] == 10
    assert page["hasNext"] is True
    assert list(page["data"]) == list(range(10, 20))
