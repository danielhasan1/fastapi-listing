from typing import Type, Optional, Dict, List

from fastapi import Request
from sqlalchemy.orm import Query

from fastapi_listing.abstracts import ListingBase
from fastapi_listing.dao.generic_dao import GenericDao
from fastapi_listing.errors import FastapiListingRequestSemanticApiException, \
    NotRegisteredApiException
from fastapi_listing.factory import strategy_factory, interceptor_factory
from fastapi_listing.interface.listing_meta_info import ListingMetaInfo
from fastapi_listing.ctyping import ListingResponseType

try:
    from pydantic import BaseModel

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel: Optional[Type] = None


class FastapiListing(ListingBase):
    """
    Core class that is responsible for running the show.
    Magic happens here!
    This class acts as Orchestrator for all the decoupled modules and strategies and runs them in strategic
    manner.

    All the dependency lives outside. This design pulls only what it needs to pull or logic requested from
    client (Anyone who is requesting for listing response using public method get_response).

    As no user oriented core logic lives inside of this class there should never be any reason to import and
    extend this class outside.
    """

    def __init__(self, request: Request = None, dao: GenericDao = None,
                 pydantic_serializer: Optional[Type[BaseModel]] = None,
                 fields_to_fetch: List[str] = None,
                 *, custom_fields: Optional[bool] = False) -> None:
        self.request = request
        self.dao = dao
        if HAS_PYDANTIC and pydantic_serializer:
            self.fields_to_fetch = list(pydantic_serializer.__fields__.keys())
        elif fields_to_fetch:
            self.fields_to_fetch = fields_to_fetch
        else:
            self.fields_to_fetch = []
        self.custom_fields = custom_fields

    @staticmethod
    def _replace_aliases(mapper: Dict[str, str], req_params: List[Dict[str, str]]) -> List[Dict[str, str]]:
        for param in req_params:
            if type(mapper[param["field"]]) is tuple:
                param["field"] = mapper[param["field"]][0]
            elif type(mapper[param["field"]]) is str:
                param["field"] = mapper[param["field"]]
            else:
                raise ValueError(f"invalid field mapper")
        return req_params

    def _apply_sorting(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        try:
            sorting_params: List[dict] = listing_meta_info.feature_params_adapter.get("sort")
        except Exception:
            raise FastapiListingRequestSemanticApiException(status_code=422, detail="Crap! Sorting went wrong.")
        temp = set(item.get("field") for item in sorting_params) - set(
            listing_meta_info.sorting_column_mapper.keys())
        if temp:
            raise NotRegisteredApiException(
                status_code=409, detail=f"Sorter(s) not registered with listing: {temp}, Did you forget to do it?")
        if sorting_params:
            sorting_params = self._replace_aliases(listing_meta_info.sorting_column_mapper, sorting_params)
        else:
            sorting_params = [listing_meta_info.default_sort_val]

        def launch_mechanics(qry):
            mecha: str = listing_meta_info.sorter_mechanic
            mecha_obj = interceptor_factory.create(mecha)
            qry = mecha_obj.apply(query=qry, strategy=listing_meta_info.sorting_strategy,
                                  sorting_params=sorting_params, extra_context=listing_meta_info.extra_context)
            return qry

        query = launch_mechanics(query)
        return query

    def _apply_filters(self, query: Query, listing_meta_info: ListingMetaInfo) -> Query:
        try:
            fltrs: List[dict] = listing_meta_info.feature_params_adapter.get("filter")
        except Exception:
            raise FastapiListingRequestSemanticApiException(status_code=422,
                                                            detail=f"Crap! Filtering went wrong.")
        temp = set(item.get("field") for item in fltrs) - set(listing_meta_info.filter_column_mapper.keys())
        if temp:
            raise NotRegisteredApiException(
                status_code=409, detail=f"Filter(s) not registered with listing: {temp}, Did you forget to do it?")

        fltrs = self._replace_aliases(listing_meta_info.filter_column_mapper, fltrs)

        def launch_mechanics(qry):
            mecha_obj = interceptor_factory.create(listing_meta_info.filter_mechanic)
            qry = mecha_obj.apply(query=qry, filter_params=fltrs, dao=self.dao,
                                  request=self.request, extra_context=listing_meta_info.extra_context)
            return qry

        query = launch_mechanics(query)
        return query

    def _paginate(self, query: Query, listing_meta_info: ListingMetaInfo) -> ListingResponseType:
        try:
            raw_params = listing_meta_info.feature_params_adapter.get("pagination")
            page_params = raw_params if raw_params else {"page": 1, "pageSize": listing_meta_info.default_page_size}
            paginator_params: dict = page_params
        except Exception as e:
            raise FastapiListingRequestSemanticApiException(status_code=422,
                                                            detail="Crap! Pagination went wrong.")
        page = listing_meta_info.paginating_strategy.paginate(query,
                                                              pagination_params=paginator_params,
                                                              extra_context=listing_meta_info.extra_context)
        return page

    def _prepare_query(self, listing_meta_info: ListingMetaInfo) -> Query:
        base_query: Query = listing_meta_info.query_strategy.get_query(request=self.request,
                                                                       dao=self.dao,
                                                                       extra_context=listing_meta_info.extra_context)
        if base_query is None or not base_query:
            raise ValueError("query strategy returned nothing Query object is expected!")
        fltr_query: Query = self._apply_filters(base_query,
                                                listing_meta_info)
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
        response: ListingResponseType = self._paginate(fnl_query, listing_meta_info)
        return response
