from fastapi import Request
from sqlalchemy.orm import Query
from json import JSONDecodeError
from typing import Type, Optional

from fastapi_listing import utils
from fastapi_listing.abstracts import TableDataPaginatingStrategy
from fastapi_listing.sorter import SortingOrderStrategy
from fastapi_listing.typing import ListingResponseType, SqlAlchemyModel
from fastapi_listing.abstracts import ListingBase, ListingServiceBase
from fastapi_listing.factory import strategy_factory
from fastapi_listing.errors import ListingFilterError, ListingSorterError
from fastapi_listing.dao.generic_dao import GenericDao
from fastapi_listing.interface.listing_meta_info import ListingMetaInfo
from fastapi_listing.factory import generic_factory
from fastapi_listing.mechanics import loader

try:
    from pydantic import BaseModel

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel: Optional[Type] = None


class FastapiListing(ListingBase):

    def __init__(self, request: Request, dao: GenericDao, pydantic_serializer: Optional[Type[BaseModel]] = None,
                 custom_fields: Optional[bool] = False) -> None:
        self.request = request
        self.dao = dao
        if HAS_PYDANTIC and pydantic_serializer:
            self.fields_to_fetch = list(pydantic_serializer.__fields__.keys())
        else:
            self.fields_to_fetch = None
        self.custom_fields = custom_fields

    def _replace_aliases(self, mapper: dict[str, str], req_params: list[dict[str, str]]) -> list[dict[str, str]]:
        req_prms_cpy = req_params.copy()
        for param in req_prms_cpy:
            param["field"] = mapper[param["field"]]
        return req_prms_cpy

    def _apply_sorting(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        try:
            sorting_params: list[dict] = utils.jsonify_query_params(self.request.query_params.get("sort"))
        except JSONDecodeError:
            raise ListingSorterError("sorter param is not a valid json!")

        if temp := set(item.get("field") for item in sorting_params) - set(
                listing_meta_info.sorting_column_mapper.keys()):
            raise ListingSorterError(f"Sorter'(s) not registered with listing: {temp}, Did you forget to do it?")
        if sorting_params:
            sorting_params = self._replace_aliases(listing_meta_info.sorting_column_mapper, sorting_params)
        else:
            sorting_params = [listing_meta_info.default_sort_val]

        # ideally sorting should only happen on one field multi field sorting puts
        # unwanted strain on table when the size is big and not really popular
        # among various clients. Still leaving room for extension won't hurt
        # by default even if client is sending multiple sorting params we prioritize
        # the latest one which is last column that client requested to sort on.
        # if user want they can implement their own asc or dsc sorting order strategy and
        # decide how they really want to apply sorting params maybe all maybe none or maybe
        # conditional sorting where if one param is applied then don't apply another specific one, etc.
        # if len(sorting_params) > 1:
        #     # todo shoot a warning here with logger type warning
        #     print(f"Default one param at a time sort allowed! choosing the latest one only in lifo manner.")
        # if sorting_params:
        #     sorting_strategy = strategy_factory.create(sorting_params[-1].get("field"),
        #                                                model=self.dao.model,
        #                                                request=self.request)
        # sorting_strategy.sort(query=query, value=default_val)

        # fix this code
        # query = sorting_strategy.sort(value=sorting_params[-1],
        #                               query=query)
        def launch_mechanics(qry):
            # for mechanics in listing_meta_info.sorter_plugins:
            #     mecha: str = mechanics.split(".")[-1]
            mecha: str = listing_meta_info.sorter_plugin
            mecha_obj = generic_factory.create(mecha)
            qry = mecha_obj.apply(query=qry, strategy=listing_meta_info.sorting_strategy,
                                  sorting_params=sorting_params, extra_context=listing_meta_info.extra_context)
            return qry

        query = launch_mechanics(query)
        return query

    # no means to send allowed filte dictionary to client as this was handled by core.
    # same goes for allowed sorts.
    # need to add that in listing response.
    # naive strategies are not registered, register them.
    # we can leave multi sorting for later release for now only allow sort on a singular field.
    # this class name is not looking to good think of a different name if possible.
    # FilterApplicationEngine
    def _apply_filters(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        try:
            fltrs: list[dict] = utils.jsonify_query_params(self.request.query_params.get("filter"))
        except JSONDecodeError:
            raise ListingFilterError(f"filter param is not a valid json!")

        if temp := set(item.get("field") for item in fltrs) - set(listing_meta_info.filter_column_mapper.keys()):
            raise ListingFilterError(f"Filter'(s) not registered with listing: {temp}, Did you forget to do it?")

        fltrs = self._replace_aliases(listing_meta_info.filter_column_mapper, fltrs)

        def launch_mechanics(qry):
            mecha_obj = generic_factory.create(listing_meta_info.filter_plugin)
            qry = mecha_obj.apply(query=qry, filter_params=fltrs, dao=self.dao,
                                  request=self.request, extra_context=listing_meta_info.extra_context)
            return qry

        query = launch_mechanics(query)
        return query

    def _paginate(self, query: Query, paginate_strategy: TableDataPaginatingStrategy,
                  extra_context: dict) -> ListingResponseType:
        page = paginate_strategy.paginate(query, self.request, extra_context)
        return page

    def _prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        base_query: Query = listing_meta_info.query_strategy.get_query(request=self.request,
                                                                       dao=self.dao,
                                                                       extra_context=listing_meta_info.extra_context)
        fltr_query: Query = self._apply_filters(base_query, listing_meta_info)
        srtd_query: Query = self._apply_sorting(fltr_query, listing_meta_info)
        return srtd_query

    @staticmethod
    def _set_vals_in_extra_context(extra_context: dict, **kwargs):
        extra_context.update(kwargs)

    def get_response(self, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        self._set_vals_in_extra_context(listing_meta_info.extra_context,
                                        field_list=self.fields_to_fetch,
                                        custom_fields=self.custom_fields
                                        )
        fnl_query: Query = self._prepare_query(listing_meta_info)
        response: ListingResponseType = self._paginate(fnl_query, listing_meta_info.paginating_strategy,
                                                       listing_meta_info.extra_context)
        return response


class ListingService(ListingServiceBase):
    filter_mapper: dict = {}
    sort_mapper: dict = {}
    # here resource creation should be based on factory and not inline as we are separating creation from usage.
    # factory should deliver sorting resource
    DEFAULT_SRT_ON: str = "created_at"
    DEFAULT_SRT_ORD: str = "dsc"
    PAGINATE_STRATEGY: str = "naive_paginator"
    QUERY_STRATEGY: str = "naive_query"
    SORTING_STRATEGY: str = "naive_sorter"
    SORT_MECHA: str = "sorter_mechanics"
    FILTER_MECHA: str = "filter_mechanics"
    dao_kls: GenericDao = GenericDao

    # pydantic_serializer: Type[BaseModel] = None
    # allowed_pydantic_custom_fields: bool = False
    # it is possible to have more than one serializer for particular endpoint depending upon
    # user or a query/path param condition we could switch json schema so allowing this
    # flexibility for the user to be able to switch between schema Fastapilisting object
    # should get initialized at user level and not implicit.

    def __init__(self, request, **kwargs) -> None:
        self.dao = self.dao_kls(**kwargs)
        # pop out db sessions as they are concrete property of data access layer and not service layer.
        # once injected to dao popping out here
        kwargs.pop("read_db", None)
        kwargs.pop("write_db", None)
        self.request = request
        self.extra_context = kwargs

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

    def page_data_modifier(self, data: dict) -> dict:
        raise NotImplementedError

    class MetaInfo:

        def __init__(self, outer_instance):
            self.paginating_strategy: TableDataPaginatingStrategy = strategy_factory.create(
                outer_instance.PAGINATE_STRATEGY)
            self.filter_column_mapper: dict = outer_instance.filter_mapper
            self.query_strategy: Query = strategy_factory.create(outer_instance.QUERY_STRATEGY)
            # self.sorting_column_mapper: dict = outer_instance.sort_mapper
            self.default_sort_val: dict[str, str] = dict(type=outer_instance.DEFAULT_SRT_ORD,
                                                         field=outer_instance.DEFAULT_SRT_ON)
            self.sorting_strategy: SortingOrderStrategy = strategy_factory.create(
                outer_instance.SORTING_STRATEGY,
                model=outer_instance.dao.model,
                request=outer_instance.request
            )
            self.sorter_plugin: str = outer_instance.SORT_MECHA
            self.filter_plugin: str = outer_instance.FILTER_MECHA
            self.extra_context: dict = outer_instance.extra_context

    def meta_info_generator(self) -> ListingMetaInfo:
        return ListingService.MetaInfo(self) # type:ignore # noqa # some issue is coming in pycharm for return types

    @classmethod
    def get_aliased_filter_mapper(cls) -> dict[str, str]:
        return {key: key for key, val in cls.filter_mapper.items()}

    @classmethod
    def get_aliased_sort_mapper(cls) -> dict[str, str]:
        return {key: key for key, val in cls.sort_mapper.items()}

    @staticmethod
    def get_sort_mecha_plugin_path() -> str:
        """
        hook to provide sort mecha plugin module path as py import path
        overwrite allowed to provide custom path.
        :return: import path as string ex. fastapi_listing.mechanics.sorter_mechanics.
        """
        return "fastapi_listing.mechanics.sorter_mechanics"

    @staticmethod
    def get_filter_mecha_plugin_path() -> str:
        """
       hook to provide filter mecha plugin module path as py import path
       overwrite allowed to provide custom path.
       :return: import path as string ex. fastapi_listing.mechanics.filter_mechanics.
       """
        return "fastapi_listing.mechanics.filter_mechanics"

    @classmethod
    def plugins_to_load(cls) -> list[str]:
        """
        Provided a hook to be called at module level of each listing service.
        overwrite sort or filter plugin path getters to give your own custom
        mechanic implementations.
        refrain from overwriting it as this may change or it's fundamnetal
        implementation is already broken down to pieces that can no longer
        be broken any further. So instead of overwriting this
        overwrite the individual pieces
        :return: list plugins to load
        currently only support sort/filter mecha loading
        todo: can add pattern calling like %s_plugin_path for providing n number of plugin loading
        """
        return [cls.get_sort_mecha_plugin_path(), cls.get_filter_mecha_plugin_path()]


# calling loader at module level so once the module is loaded all plugins get loaded and not further loading is required
loader.load_plugins(ListingService.plugins_to_load())


# todo: how to provide a hook in listing service so a person can easily overwrite the data list or manipulate it easily
# todo: before wrapping it up in page response

