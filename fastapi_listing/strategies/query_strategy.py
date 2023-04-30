from fastapi_listing.abstracts import QueryStrategy
from fastapi_listing.dao import GenericDao
from fastapi_listing.typing import SqlAlchemyQuery, FastapiRequest


class NaiveQueryStrategy(QueryStrategy):

    def get_inst_attr_to_read(self, custom_fields: bool, field_list: list, dao: GenericDao):
        inst_fields = []

        if custom_fields:
            # ("BYPASS CUSTOM PYDANTIC FIELDS ALLOWED.")
            # when serializer contains fields that get filled via validators or at runtime
            # or fields that get generated from model fields.
            for field in field_list:
                try:
                    inst_fields.append(getattr(field, dao.model))
                except AttributeError:
                    pass
        else:
            inst_fields = [getattr(dao.model, field) for field in field_list]
        return inst_fields

    def get_query(self, *, request: FastapiRequest = None, dao: GenericDao = None,
                  extra_context: dict = None) -> SqlAlchemyQuery:
        inst_fields = self.get_inst_attr_to_read(extra_context.get("custom_fields"), extra_context.get("field_list"),
                                                 dao)
        query = dao.get_naive_read(inst_fields)
        return query
