from typing import Dict

from fastapi_listing.abstracts import AbsSortingStrategy
from fastapi_listing.context import QueryContext
from fastapi_listing.ctyping import FastapiRequest
from fastapi_listing.factory import _generic_factory


class SortingOrderStrategy(AbsSortingStrategy):
    """
    Backend-agnostic by construction: it only ever resolves a field name to
    whatever object the backend's model/registered extractor gives back
    (a SQLAlchemy InstrumentedAttribute, a plain ClickHouse column-name
    string, ...) and hands both the field and the "asc"/"dsc" direction to
    the QueryContext - which is the only place that knows how to turn that
    into native syntax.
    """

    def __init__(self, model=None, request: FastapiRequest = None):
        self.model = model
        self.request = request

    def sort(self, *, context: QueryContext = None, value: Dict[str, str] = None,
             extra_context: dict = None) -> QueryContext:
        assert value["type"] in ["asc", "dsc"], "invalid sorting style!"
        inst_field = self.validate_srt_field(self.model, value["field"])
        return context.order_by(field=inst_field, direction=value["type"])

    def validate_srt_field(self, model, sort_field: str):
        field = sort_field.split(".")[-1]
        if sort_field in _generic_factory.object_creation_collector:
            inst_field = _generic_factory.create(sort_field, field)
        else:
            try:
                inst_field = getattr(model, field)
            except AttributeError:
                inst_field = None
            if inst_field is None:
                raise ValueError(
                    f"Provided sort field {field!r} is not an attribute of {model.__name__}")  # todo improve this by custom exception
        return inst_field
