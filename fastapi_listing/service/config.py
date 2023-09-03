from typing import Literal, Optional, TypedDict, Type

# from fastapi_listing.interface.listing_meta_info import ListingMetaData
from fastapi_listing.service.adapters import CoreListingParamsAdapter


class ListingMetaData(TypedDict):
    filter_mapper: dict
    sort_mapper: dict
    default_srt_ord: Literal["asc", "dsc"]
    default_srt_on: str
    paginating_strategy: str
    query_strategy: str
    sorting_strategy: str
    sort_mecha: str
    filter_mecha: str
    default_page_size: int
    max_page_size: int
    feature_params_adapter: Type[CoreListingParamsAdapter]
    allow_count_query_by_paginator: bool
    extra_context: dict


def MetaInfo(
        *,
        filter_mapper: Optional[dict] = None,
        sort_mapper: Optional[dict] = None,
        default_srt_ord: Literal["asc", "dsc"] = "dsc",
        default_srt_on: str,
        paginating_strategy: str = "default_paginator",
        query_strategy: str = "default_query",
        sorting_strategy: str = "default_sorter",
        sort_mecha: str = "indi_sorter_interceptor",
        filter_mecha: str = "iterative_filter_interceptor",
        default_page_size: int = 10,
        max_page_size: int = 50,
        feature_params_adapter=CoreListingParamsAdapter,
        allow_count_query_by_paginator: bool = True,
        **kwargs) -> ListingMetaData:
    """validate passed args"""
    if default_srt_ord not in ["asc", "dsc"]:
        raise ValueError(f"default_srt_ord is incorrect expected 'Literal['asc', 'dsc']' got {default_srt_ord!r}")
    if not filter_mapper:
        filter_mapper = dict()
    if not sort_mapper:
        sort_mapper = dict()
    extra_context = kwargs or dict()
    return ListingMetaData(filter_mapper=filter_mapper,
                           sort_mapper=sort_mapper,
                           default_srt_ord=default_srt_ord,
                           default_srt_on=default_srt_on,
                           paginating_strategy=paginating_strategy,
                           query_strategy=query_strategy,
                           sorting_strategy=sorting_strategy,
                           sort_mecha=sort_mecha,
                           filter_mecha=filter_mecha,
                           default_page_size=default_page_size,
                           max_page_size=max_page_size,
                           feature_params_adapter=feature_params_adapter,
                           allow_count_query_by_paginator=allow_count_query_by_paginator,
                           extra_context=extra_context)
