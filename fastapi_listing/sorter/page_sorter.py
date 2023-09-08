from typing import Dict
from fastapi_listing.abstracts import AbsSortingStrategy
from fastapi_listing.ctyping import SqlAlchemyModel, FastapiRequest, SqlAlchemyQuery, AnySqlAlchemyColumn
from fastapi_listing.factory import _generic_factory


class SortingOrderStrategy(AbsSortingStrategy):

    def __init__(self, model: SqlAlchemyModel = None, request: FastapiRequest = None):
        self.model = model
        self.request = request

    @staticmethod
    def sort_asc_util(query: SqlAlchemyQuery, inst_field: AnySqlAlchemyColumn) -> SqlAlchemyQuery:
        query = query.order_by(inst_field.asc())
        return query

    @staticmethod
    def sort_dsc_util(query: SqlAlchemyQuery, inst_field: AnySqlAlchemyColumn) -> SqlAlchemyQuery:
        query = query.order_by(inst_field.desc())
        return query

    def sort(self, *, query: SqlAlchemyQuery = None, value: Dict[str, str] = None,
             extra_context: dict = None) -> SqlAlchemyQuery:
        assert value["type"] in ["asc", "dsc"], "invalid sorting style!"
        inst_field: AnySqlAlchemyColumn = self.validate_srt_field(self.model, value["field"])
        if value["type"] == "asc":
            query = self.sort_asc_util(query, inst_field)
        else:
            query = self.sort_dsc_util(query, inst_field)
        return query

    def validate_srt_field(self, model: SqlAlchemyModel, sort_field: str):
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
