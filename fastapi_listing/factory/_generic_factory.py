"""Factory for creating a game character."""

from typing import Any, Callable

object_creation_collector: dict[str, Callable[..., Any]] = {}


def register(key: str, creator: Callable[..., Any]) -> None:
    print(creator)
    """Register a new game character type."""
    if key in object_creation_collector:
        raise ValueError(f"Factory can not have duplicate builder key {key} for instance {creator.__name__}")
    object_creation_collector[key] = creator


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
