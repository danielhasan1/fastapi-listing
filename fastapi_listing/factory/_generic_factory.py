"""Factory for creating a game character."""

from typing import Any, Callable, Dict
import types

object_creation_collector: Dict[str, Callable[..., Any]] = {}


def register(key: str, creator: Callable[..., Any]) -> None:
    """Register a new game character type."""
    if key in object_creation_collector:
        raise ValueError(f"Factory can not have duplicate builder key {key} for instance {creator.__name__}")
    object_creation_collector[key] = creator


def is_mapper_semantic_valid(mapper_val):
    if type(mapper_val) is not tuple:
        raise ValueError("Invalid sorter mapper semantic! Expected tuple!")
    if len(mapper_val) != 2:
        raise ValueError(f"Invalid sorter mapper semantic {mapper_val}! min tuple length should be 2.")
    if type(mapper_val[0]) is not str:
        raise ValueError(f"Invalid sorter mapper semantic {mapper_val}! first tuple element should be field (str)")
    if not isinstance(mapper_val[1], types.FunctionType):
        raise ValueError(f"positional arg error, expects a callable but received: {mapper_val[1]}!")
    return True


def register_sort_mapper(mapper_val):
    if is_mapper_semantic_valid(mapper_val):
        register(mapper_val[0], mapper_val[1])


def unregister(key: str) -> None:
    """Unregister a game character type."""
    object_creation_collector.pop(key, None)


def create(builder_key: str, *args, **kwargs) -> Any:
    """Create a game character of a specific type, given JSON data."""
    try:
        creator = object_creation_collector[builder_key]
    except KeyError:
        raise ValueError(f"unknown character type {builder_key!r}")
    return creator(*args, **kwargs)
