"""Error/edge branches on the registries that were never exercised without a
real MySQL connection getting in the way first."""

import pytest

from fastapi_listing.factory import strategy_factory
from fastapi_listing.factory import _generic_factory
from fastapi_listing.abstracts import AbsQueryStrategy


def test_strategy_factory_rejects_non_strategy_builder():
    with pytest.raises(ValueError, match="is not a valid type of strategy"):
        strategy_factory.register_strategy("not_a_strategy_test_key", object)


def test_strategy_factory_create_unknown_key_raises():
    with pytest.raises(ValueError, match="no strategy found with name"):
        strategy_factory.create("definitely_unregistered_strategy_key")


def test_strategy_factory_accepts_a_real_strategy_subclass():
    class _FakeQueryStrategy(AbsQueryStrategy):
        def get_query(self, *, request=None, dao=None, extra_context=None):
            return "fake-context"

    strategy_factory.register_strategy("fake_query_strategy_edge_case_test", _FakeQueryStrategy)
    instance = strategy_factory.create("fake_query_strategy_edge_case_test")
    assert isinstance(instance, _FakeQueryStrategy)


def test_generic_factory_unregister_removes_a_registered_key():
    _generic_factory.register("unregister_edge_case_test", lambda x: x)
    assert "unregister_edge_case_test" in _generic_factory.object_creation_collector
    _generic_factory.unregister("unregister_edge_case_test")
    assert "unregister_edge_case_test" not in _generic_factory.object_creation_collector


def test_generic_factory_unregister_unknown_key_is_a_noop():
    _generic_factory.unregister("never_registered_key_edge_case_test")  # should not raise
