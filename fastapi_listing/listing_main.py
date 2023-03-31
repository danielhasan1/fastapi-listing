from typing import Type, Optional
from fastapi import Request
from sqlalchemy.orm import Query
from json import JSONDecodeError

from fastapi_listing import utils
from fastapi_listing.sorter import SortingOrderStrategy
from fastapi_listing.paginator import NaivePaginationStrategy
from fastapi_listing.typing import ListingResponseType
from fastapi_listing.abstracts import ListingBase, ListingMetaInfo
from fastapi_listing.factory import strategy_factory, filter_factory
from fastapi_listing.errors import ListingFilterError, ListingSorterError
from fastapi_listing.filters import CommonFilterImpl
from fastapi_listing.generic_dao import GenericDao


try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel: Optional[Type] = None


class FastapiListing(ListingBase):

    def __init__(self, request: Request, dao: GenericDao, pydantic_serializer: Type[BaseModel] = None,
                 custom_fields: bool = False) -> None:
        self.request = request
        self.dao = dao
        if HAS_PYDANTIC:
            self.fields_to_fetch = list(pydantic_serializer.__fields__.keys())
        else:
            self.fields_to_fetch = None # can't deduce automatically tell this in query strategy
        self.custom_fields = custom_fields

    def apply_sorting(self, query: Query, sorting_strategy: SortingOrderStrategy,
                      sort_field_mapper: dict[str, str]) -> Query:
        query = sorting_strategy.sort(query=query, request=self.request, model=self.dao.model,
                                      field_mapper=sort_field_mapper)
        return query

    # no means to send allowed filte dictionary to client as this was handled by core.
    # same goes for allowed sorts.
    # need to add that in listing response.
    # naive strategies are not registered, register them.
    # we can leave multi sorting for later release for now only allow sort on a singular field.
    # this class name is not looking to good think of a different name if possible.
    def apply_filters(self, query: Query, filter_field_mapper: dict[str, str]) -> Query:
        try:
            fltrs: list[dict] = utils.jsonify_query_params(self.request.query_params.get("filter"))
        except JSONDecodeError as e:
            raise ListingFilterError(f"filter param is not a valid json!")
        for applied_filter in fltrs:
            if applied_filter.get("field") not in filter_field_mapper:
                raise ListingFilterError("Filter not registered with listing! Did you forget to do it?")
            filter_obj: CommonFilterImpl = filter_factory.create(filter_field_mapper[applied_filter.get("field")],
                                                                 dao=self.dao,
                                                                 request=self.request)
            query = filter_obj.filter(field=filter_field_mapper[applied_filter.get("field")],
                                      value=applied_filter.get("value"),
                                      query=query)
        return query

    def paginate(self, query: Query, paginate_strategy: NaivePaginationStrategy) -> ListingResponseType:
        query = paginate_strategy.paginate(query, self.request)
        return query

    def prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        base_query: Query = listing_meta_info.query_strategy.get_query(field_list=self.fields_to_fetch,
                                                                       request=self.request,
                                                                       dao=self.dao,
                                                                       custom_fields=self.custom_fields)
        fltr_query: Query = self.apply_filters(base_query, listing_meta_info.filter_column_mapper)
        srtd_query: Query = self.apply_sorting(fltr_query, listing_meta_info.sorting_strategy,
                                               listing_meta_info.sorting_column_mapper)
        return srtd_query

    def prepare_response(self, query, paginating_strategy) -> ListingResponseType:
        """
        A hook that allows us to perform pre paginating alterations when inheriting.
        Could be use to alter query just before pagination on some conditional basis when
        one doesn't need to interact with metainfo.
        Could be used to alter response format only.
        Encapsulates one to only see what they need to.
        :param query: sqlalchemy Query object
        :param paginating_strategy: pagination object for paginating query response
        :return: Page with listing data for rendering at client.
        """
        pgntd_resp: ListingResponseType = self.paginate(query, paginating_strategy)
        return pgntd_resp

    def get_response(self, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        fnl_query: Query = self.prepare_query(listing_meta_info)
        response: ListingResponseType = self.prepare_response(fnl_query, listing_meta_info.paginating_strategy)
        return response


class ListingService:
    filter_mapper = {}
    sort_mapper = {}
    # here resource creation should be based on factory and not inline as we are separating creation from usage.
    # factory should deliver sorting resource
    DEFAULT_SRT_ON = "created_at"
    SRT_STRATEGY_ASC = "naive_srt_asc"
    SRT_STRATEGY_DSC = "naive_srt_dsc"
    PAGINATE_STRATEGY = "naive_pagination"
    QUERY_STRATEGY = "naive_query"

    def __init__(self, dao, request, model, **kwargs):
        self.dao = dao(model, **kwargs)
        self.request = request

    def get_listing(self):
        raise NotImplementedError

    def choose_sorting_strategy(self):
        try:
            sorting_param: list[dict] = utils.jsonify_query_params(self.request.query_params.get("sort"))
        except JSONDecodeError as e:
            # CashifyLogger.error(f"Error occurred during sort decode:{e}")
            raise ListingSorterError("sorter param is not a valid json!")
        srt_strtg: str = ""
        if sorting_param:
            srt_strtg = sorting_param[0].get("type")
        if srt_strtg == "asc":
            return strategy_factory.create(self.SRT_STRATEGY_ASC, self.DEFAULT_SRT_ON)
        else:
            return strategy_factory.create(self.SRT_STRATEGY_DSC, self.DEFAULT_SRT_ON)

    class MetaInfo:
        def __init__(self, outer_instance):
            self.outer_instance: ListingService = outer_instance
            self.sorting_strategy = outer_instance.choose_sorting_strategy()
            self.paginating_strategy = strategy_factory.create(
                outer_instance.PAGINATE_STRATEGY)
            self.filter_column_mapper = outer_instance.filter_mapper
            self.query_strategy = strategy_factory.create(outer_instance.QUERY_STRATEGY)
            self.sorting_column_mapper = outer_instance.sort_mapper

    def create_inner(self) -> MetaInfo:
        return ListingService.MetaInfo(self)

    @classmethod
    def get_aliased_filter_mapper(cls) -> dict[str, str]:
        return {key: key for key, val in cls.filter_mapper.items()}

    @classmethod
    def get_aliased_sort_mapper(cls) -> dict[str, str]:
        return {key: key for key, val in cls.sort_mapper.items()}