from typing_extensions import get_args
from typing import Type, TypeVar, Union

from fastapi_listing.abstracts import AbsQueryStrategy, AbsSortingStrategy, AbsPaginatingStrategy

x = Union[AbsQueryStrategy, AbsSortingStrategy, AbsPaginatingStrategy]

T = TypeVar("T", AbsPaginatingStrategy, AbsSortingStrategy, AbsQueryStrategy)


class StrategyObjectFactory:
    def __init__(self):
        self._strategy = {}

    def register_strategy(self, key: str, builder: type):
        if key is None or not key:
            raise ValueError("Invalid type key!")
        if key in self._strategy:
            raise ValueError(f"strategy name: {key}, already in use with {self._strategy[key].__name__}!")
        if not issubclass(builder, get_args(x)):
            raise ValueError(f"builder {builder!r} is not a valid type of strategy, allowed {x}")
        self._strategy[key] = builder

    def create(self, key: str, *args, **kwargs) -> T:
        strategy_: Type[T] = self._strategy.get(key)
        if not strategy_:
            raise ValueError(f"no strategy found with name {key!r} in strategy_factory")
        return strategy_(*args, **kwargs)

    def aware_of(self, key: str) -> bool:
        return key in self._strategy


strategy_factory = StrategyObjectFactory()
