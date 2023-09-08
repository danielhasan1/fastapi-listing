from typing import Optional, Type

try:
    from typing import Literal, TypedDict
except ImportError:
    from typing_extensions import Literal, TypedDict

from fastapi_listing.service.adapters import CoreListingParamsAdapter


class ListingMetaData(TypedDict):
    """A Typedict for configuring fastapi-listing behaviour"""

    filter_mapper: dict
    """
    The filter_mapper is a collection of allowed filters on listing that will be used by consumers. Defaults to '{}'
    """

    sort_mapper: dict
    """
    The sort_mapper is a collection of fields allowed to be used for sort on listing that will be used by consumer.
    Defaults to '{}'
    """

    default_srt_on: str
    """primary model field that will be used to sort the listing response by default. No Default value provided."""

    default_srt_ord: Literal["asc", "dsc"]
    """The default order which will be used to return listing response. Defaults to 'dsc' """

    paginating_strategy: str
    """
    Reference of strategy class used to paginate listing response. Must be registered with strategy_factory.
    Defaults to 'default_paginator'
    """

    query_strategy: str
    """
    Reference of strategy class used to generate listing query object. Must be registered with strategy_factory.
    Defaults to 'default_query'
    """

    sorting_strategy: str
    """
    Reference of strategy class used to apply sorting on query object. Must be registered with strategy_factory.
    Defaults to 'default_sorter'
    """

    sort_mecha: str
    """
    Reference of interceptor class that applies sorting requested by client utilising sort_mapper.
    Must be registered with interceptor_factory.
    Defaults to 'indi_sorter_interceptor'
    """

    filter_mecha: str
    """
    Reference of interceptor class that applies filter requested by client utilising filter_mapper.
    Must be registered with interceptor factory.
    Defaults to 'iterative_filter_interceptor'
    """

    default_page_size: int
    """The default number of items that a page should contain. Defaults to '10' """

    max_page_size: int
    """
    Maximum number of items that a page should contain. Ignore any upper page size limit than this.
    Defaults to '50'
    """

    feature_params_adapter: Type[CoreListingParamsAdapter]
    """
    Reference of the adapter class used to get listing feature(filter/sorter/paginator) parameters.
    Lets users make fastapi-listing adapt to their current code base.
    Defaults to 'CoreListingParamsAdapter'
    """

    allow_count_query_by_paginator: bool
    """
    Restrict/Allow fastapi-listing default paginator to extract total count. This lets you avoid slow
    count queries on big table to avoid performance hiccups.
    Defaults to 'True'
    """

    extra_context: dict
    """
    A common datastructure used to store any context data that a user may wanna pass from router.
    Like path params or query params or anything.
    Available throughout the entire fastapi-listing lifespan.
    User can access it in
    strategies
    interceptors
    filters
    or almost anywhere in their code where they are writing their listing API dependency using/extending fastapi-listing
    core features.
    Defaults to '{}'
    """


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
        **extra) -> ListingMetaData:
    """validate passed args"""
    if default_srt_ord not in ["asc", "dsc"]:
        raise ValueError(f"default_srt_ord is incorrect expected 'Literal['asc', 'dsc']' got {default_srt_ord!r}")
    if not filter_mapper:
        filter_mapper = dict()
    if not sort_mapper:
        sort_mapper = dict()
    extra_context = extra or dict()
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
