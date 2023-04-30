from fastapi_listing.abstracts import TableDataSortingStrategy
from fastapi_listing.typing import SqlAlchemyModel, FastapiRequest, SqlAlchemyQuery, AnySqlAlchemyColumn


class SortingOrderStrategy(TableDataSortingStrategy):

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

    def sort(self, *, query: SqlAlchemyQuery = None, value: dict[str, str] = None,
             extra_context: dict = None) -> SqlAlchemyQuery:
        assert value["type"] in ["asc", "dsc"]
        if value is None:
            raise ValueError("sort expects value with structure [type, field], none provided")
        inst_field: AnySqlAlchemyColumn = self.validate_srt_field(self.model, value["field"])
        if value["type"] == "asc":
            query = self.sort_asc_util(query, inst_field)
        else:
            query = self.sort_dsc_util(query, inst_field)
        return query

    @staticmethod
    def validate_srt_field(model: SqlAlchemyModel, sort_field: str):
        try:
            inst_field = getattr(model, sort_field)
        except AttributeError:
            inst_field = None
        if inst_field is None:
            raise ValueError(
                f"Provided sort field is not an attribute of {model}")  # todo improve this by custom exception
        return inst_field
