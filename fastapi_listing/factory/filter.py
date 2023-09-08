from typing import Dict, Tuple, Optional, Callable
import inspect
import types

from fastapi_listing.filters.generic_filters import CommonFilterImpl
from fastapi_listing.ctyping import AnySqlAlchemyColumn


class FilterObjectFactory:
    def __init__(self):
        self._filters = {}

    def register_filter(self, key: str, builder: CommonFilterImpl,
                        field_extractor_fn: Callable[[str], AnySqlAlchemyColumn] = None):
        if key is None or not key:
            raise ValueError("Invalid type key!")
        if key in self._filters:
            raise ValueError(f"filter key {key!r} already in use with {self._filters[key][0].__name__!r}")
        self._filters[key] = (builder, field_extractor_fn)

    def is_mapper_semantic_valid(self, mapper_val):
        if type(mapper_val) is not tuple:
            raise ValueError("Invalid filter mapper semantic! Expected tuple!")
        if len(mapper_val) < 2 or len(mapper_val) > 3:
            raise ValueError(f"Invalid filter mapper semantic {mapper_val}! min tuple length should be 2.")
        if type(mapper_val[0]) is not str:
            raise ValueError(f"Invalid filter mapper semantic {mapper_val}! first tuple element should be field (str)")
        if not inspect.isclass(mapper_val[1]):
            raise ValueError(f"Invalid filter mapper semantic {mapper_val[1]!r}! Expects a class!")
        if not issubclass(mapper_val[1], CommonFilterImpl) and mapper_val[1] != CommonFilterImpl:
            raise ValueError(f"Invalid filter mapper semantic {mapper_val[1]!r}!"
                             f" Expects a subclass of CommonFilterImpl")
        if len(mapper_val) == 3 and not isinstance(mapper_val[2], types.FunctionType):
            raise ValueError(f"positional arg error, expects a callable but received: {mapper_val[2]!r}!")
        return True

    def register_filter_mapper(
            self, filter_mapper: Dict[str, Tuple[str, CommonFilterImpl, Optional[Callable[[str], AnySqlAlchemyColumn]]]]
    ):
        for key, val in filter_mapper.items():
            if self.is_mapper_semantic_valid(val):
                self.register_filter(val[0], *val[1:])

    def create(self, key: str, **kwargs):
        try:
            filter_, field_extractor_fn = self._filters[key]
        except KeyError:
            raise ValueError(f"filter factory couldn't find registered key {key!r}")
        return filter_(**kwargs, field_extract_fn=field_extractor_fn)


filter_factory = FilterObjectFactory()
