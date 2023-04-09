from typing import Type, Optional
from fastapi import Request
from sqlalchemy.orm import Query
from json import JSONDecodeError

from fastapi_listing import utils
from fastapi_listing.abstracts import TableDataPaginatingStrategy, TableDataSortingStrategy
from fastapi_listing.sorter import SortingOrderStrategy
from fastapi_listing.typing import ListingResponseType
from fastapi_listing.abstracts import ListingBase, ListingMetaInfo
from fastapi_listing.factory import strategy_factory, filter_factory
from fastapi_listing.errors import ListingFilterError, ListingSorterError
from fastapi_listing.filters import CommonFilterImpl
from fastapi_listing.generic_dao import GenericDao
from fastapi_listing.plugins import loader
from fastapi_listing.factory import generic_factory

try:
    from pydantic import BaseModel

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel: Optional[Type] = None

N_SRT_STRATEGY_DSC = "naive_sort_dsc"
N_SRT_STRATEGY_ASC = "naive_sort_asc"


class FastapiListing(ListingBase):

    def __init__(self, request: Request, dao: GenericDao, pydantic_serializer: Type[BaseModel] = None,
                 custom_fields: bool = False) -> None:
        self.request = request
        self.dao = dao
        if HAS_PYDANTIC:
            self.fields_to_fetch = list(pydantic_serializer.__fields__.keys())
        else:
            self.fields_to_fetch = None  # can't deduce automatically tell this in query strategy
        self.custom_fields = custom_fields

    def replace_aliases(self, mapper: dict[str, str], req_params: list[dict[str, str]]) -> list[dict[str, str]]:
        req_prms_cpy = req_params.copy()
        for param in req_prms_cpy:
            param["field"] = mapper[param["field"]]
        return req_prms_cpy

    def apply_sorting(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        try:
            sorting_params: list[dict] = utils.jsonify_query_params(self.request.query_params.get("sort"))
        except JSONDecodeError:
            raise ListingSorterError("sorter param is not a valid json!")

        if temp := set(item.get("field") for item in sorting_params) - set(
                listing_meta_info.sorting_column_mapper.keys()):
            raise ListingSorterError(f"Sorter'(s) not registered with listing: {temp}, Did you forget to do it?")
        if sorting_params:
            sorting_params = self.replace_aliases(listing_meta_info.sorting_column_mapper, sorting_params)
        else:
            sorting_params = [listing_meta_info.default_sort_val]
        loader.load_plugins(listing_meta_info.sorter_plugins)

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
            mecha: str = listing_meta_info.sorter_plugins[-1].split(".")[-1]
            mecha_obj = generic_factory.create(mecha, query=qry, strategy=listing_meta_info.sorting_strategy,
                                               sorting_params=sorting_params)
            qry = mecha_obj.apply()
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
    def apply_filters(self, query: Query, filter_field_mapper: dict[str, str], filter_plugins: list[str]) -> Query:
        try:
            fltrs: list[dict] = utils.jsonify_query_params(self.request.query_params.get("filter"))
        except JSONDecodeError:
            raise ListingFilterError(f"filter param is not a valid json!")

        if temp := set(item.get("field") for item in fltrs) - set(filter_field_mapper.keys()):
            raise ListingFilterError(f"Filter'(s) not registered with listing: {temp}, Did you forget to do it?")

        fltrs = self.replace_aliases(filter_field_mapper, fltrs)

        loader.load_plugins(filter_plugins)

        def launch_mechanics(qry):
            mecha: str = filter_plugins[-1].split(".")[-1]
            mecha_obj = generic_factory.create(mecha, query=qry, filter_params=fltrs, dao=self.dao,
                                               request=self.request)
            qry = mecha_obj.apply()
            return qry

        query = launch_mechanics(query)

        # for applied_filter in fltrs:
        #     filter_obj: CommonFilterImpl = filter_factory.create(filter_field_mapper[applied_filter.get("field")],
        #                                                          dao=self.dao,
        #                                                          request=self.request)
        #     query = filter_obj.filter(field=filter_field_mapper[applied_filter.get("field")],
        #                               value=applied_filter.get("value"),
        #                               query=query)
        return query

    def paginate(self, query: Query, paginate_strategy: TableDataPaginatingStrategy) -> ListingResponseType:
        query = paginate_strategy.paginate(query, self.request)
        return query

    def prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        base_query: Query = listing_meta_info.query_strategy.get_query(field_list=self.fields_to_fetch,
                                                                       request=self.request,
                                                                       dao=self.dao,
                                                                       custom_fields=self.custom_fields)
        fltr_query: Query = self.apply_filters(base_query, listing_meta_info.filter_column_mapper)
        srtd_query: Query = self.apply_sorting(fltr_query, listing_meta_info)
        return srtd_query

    # def prepare_response(self, query, paginating_strategy) -> ListingResponseType:
    #     """
    #     Prepares a page response to return to the client
    #     :param query sqlalchemy query
    #     """
    #     pgntd_resp: ListingResponseType = self.paginate(query, paginating_strategy)
    #     return pgntd_resp

    def get_response(self, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        fnl_query: Query = self.prepare_query(listing_meta_info)
        response: ListingResponseType = self.paginate(fnl_query, listing_meta_info.paginating_strategy)
        return response


class ListingService:
    filter_mapper = {}
    sort_mapper = {}
    # here resource creation should be based on factory and not inline as we are separating creation from usage.
    # factory should deliver sorting resource
    DEFAULT_SRT_ON = "created_at"
    DEFAULT_SRT_ORD = "dsc"
    PAGINATE_STRATEGY = "naive_paginator"
    QUERY_STRATEGY = "naive_query"
    SORTING_STRATEGY = "naive_sorter"
    SORTER_PLUGIN = ["fastapi_listing.plugins.sorter_mechanics"]
    FILTER_PLUGIN = ["fastapi_listing.plugins.filter_mechanics"]

    def __init__(self, dao, request, model, **kwargs):
        self.dao = dao(model, **kwargs)
        self.request = request

    def get_listing(self):
        raise NotImplementedError

    # def choose_sorting_strategy(self):
    #     try:
    #         sorting_param: list[dict] = utils.jsonify_query_params(self.request.query_params.get("sort"))
    #     except JSONDecodeError:
    #         # CashifyLogger.error(f"Error occurred during sort decode:{e}")
    #         raise ListingSorterError("sorter param is not a valid json!")
    #     srt_strtg: str = "dsc"
    #     if sorting_param:
    #         srt_strtg = sorting_param[-1].get("type")
    #     if srt_strtg == "asc":
    #         return strategy_factory.create(self.SRT_STRATEGY_ASC, self.DEFAULT_SRT_ON)
    #     else:
    #         return strategy_factory.create(self.SRT_STRATEGY_DSC, self.DEFAULT_SRT_ON)

    class MetaInfo:
        def __init__(self, outer_instance) -> None:
            # self.sorting_strategy = outer_instance.choose_sorting_strategy()
            self.paginating_strategy: TableDataPaginatingStrategy = strategy_factory.create(
                outer_instance.PAGINATE_STRATEGY)
            self.filter_column_mapper: dict = outer_instance.filter_mapper
            self.query_strategy: Query = strategy_factory.create(outer_instance.QUERY_STRATEGY)
            self.sorting_column_mapper: dict = outer_instance.sort_mapper
            self.default_sort_val: dict[str, str] = dict(type=outer_instance.DEFAULT_SRT_ORD,
                                                         field=outer_instance.DEFAULT_SRT_ON)
            self.sorting_strategy: SortingOrderStrategy = strategy_factory.create(
                outer_instance.SORTING_STRATEGY,
                model=outer_instance.dao.model,
                request=outer_instance.request
            )
            self.sorter_plugins = outer_instance.SORTER_PLUGIN
            self.filter_plugins = outer_instance.FILTER_PLUGIN

    def create_inner(self) -> MetaInfo:
        return ListingService.MetaInfo(self)

    @classmethod
    def get_aliased_filter_mapper(cls) -> dict[str, str]:
        return {key: key for key, val in cls.filter_mapper.items()}

    @classmethod
    def get_aliased_sort_mapper(cls) -> dict[str, str]:
        return {key: key for key, val in cls.sort_mapper.items()}

# default strategy factory
