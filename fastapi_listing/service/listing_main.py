from typing import Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi import Request

from fastapi_listing.abstracts import ListingServiceBase
from fastapi_listing.dao.generic_dao import GenericDao
from fastapi_listing.dao import dao_factory
from fastapi_listing.service.adapters import CoreListingParamsAdapter
from fastapi_listing.errors import MissingSessionError
from fastapi_listing.service.config import ListingMetaData


__all__ = [
    "ListingService"
]


class ListingService(ListingServiceBase):  # noqa
    filter_mapper: dict = {}
    sort_mapper: dict = {}
    # here resource creation should be based on factory and not inline as we are separating creation from usage.
    # factory should deliver sorting resource
    # default_srt_on: str = "created_at" # to be taken by user at child class level
    default_srt_ord: Literal["asc", "dsc"] = "dsc"
    paginate_strategy: str = "default_paginator"
    query_strategy: str = "default_query"
    sorting_strategy: str = "default_sorter"
    sort_mecha: str = "indi_sorter_interceptor"
    filter_mecha: str = "iterative_filter_interceptor"
    default_page_size: int = 10
    max_page_size: int = 50
    default_dao: GenericDao = GenericDao
    feature_params_adapter = CoreListingParamsAdapter
    allow_count_query_by_paginator: bool = True

    # pydantic_serializer: Type[BaseModel] = None
    # allowed_pydantic_custom_fields: bool = False
    # it is possible to have more than one serializer for particular endpoint depending upon
    # user or a query/path param condition we could switch json schema so allowing this
    # flexibility for the user to be able to switch between schema Fastapilisting object
    # should get initialized at user level and not implicit.

    def __init__(self, request: Optional[Request] = None,
                 *,
                 read_db=None,
                 write_db=None,
                 **kwargs) -> None:
        self.request = request
        self.extra_context = kwargs
        try:
            dao = dao_factory.create(self.default_dao.name)
        except MissingSessionError:
            if not read_db:
                raise MissingSessionError
            dao = self.default_dao(read_db=read_db, write_db=write_db)
        self.dao = dao

    def get_listing(self):
        """
        implement at child class level.

        FastapiListing(self.request, self.dao, pydantic_serializer=some_pydantic_model_class,
         custom_fields=True/False).get_response(self.MetaInfo(self))
        custom_fields can be also called pydantic_custom_fields.
        Note: what is pydantic_custom_fields?
                These are the fields that gets generated at runtime from existing table/sqlalchemy model fields.
                for example:
                lets say you have a pydantic model class
                class abc(BaseModel):
                    id: int
                    code: str

                    @root_validator
                    def generate_code(cls, values):
                        values["code"] = f'FANCY{values["id"]}CODE'
                here code gets generated at runtime, code is not a table field, code is a custom field that is
                deduced with the help of id.
        :return: page response for client to render
        """
        raise NotImplementedError("method should be implemented in child class and not here!")

    def MetaInfo(self, self_copy):
        """to support older versions"""
        return ListingMetaData(filter_mapper=self.filter_mapper,  # type: ignore
                               sort_mapper=self.sort_mapper,
                               default_srt_ord=self.default_srt_ord,
                               default_srt_on=self.default_srt_on,
                               paginating_strategy=self.paginate_strategy,
                               query_strategy=self.query_strategy,
                               sorting_strategy=self.sorting_strategy,
                               sort_mecha=self.sort_mecha,
                               filter_mecha=self.filter_mecha,
                               default_page_size=self.default_page_size,
                               max_page_size=self.max_page_size,
                               feature_params_adapter=self.feature_params_adapter,
                               allow_count_query_by_paginator=self.allow_count_query_by_paginator,
                               extra_context=self.extra_context)
