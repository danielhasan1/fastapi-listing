from fastapi_listing.abstracts import AbsPaginatingStrategy
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest, ListingResponseType


class PaginationStrategy(AbsPaginatingStrategy):
    """
    Loosely coupled paginator module.
    Type of page should always be maintained for core service to make sense of a page for any post page
    spawn processing.
    Clients are advised to use any adapter in their listing service for refactoring page response as per
    their needs or having a different response structure.
    """

    name = "default_paginator"

    def __init__(self, request: FastapiRequest):
        self.request = request

    def get_count(self, query: SqlAlchemyQuery) -> int:
        """
        Override this method to return a dummy count or generate count in more optimized manner.
        User may want this to avoid slow count(*) query or double query or have page setup that doesn't require
        total_counts.
        Overall special checks needs to be setup.
        like returning a massive dummy count and then depending upon empty main_data avoiding trip to next page etc.
        """
        return query.count()

    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict) -> ListingResponseType:
        count: int = self.get_count(query)
        has_next: bool = True if count - ((pagination_params.get('page')) * pagination_params.get('pageSize')
                                    ) > pagination_params.get('pageSize') else False
        current_page_size: int = pagination_params.get("pageSize")
        current_page_number: int = pagination_params.get("page")
        query = query.limit(
            pagination_params.get('pageSize')
        ).offset(
            max(pagination_params.get('page') - 1, 0) * pagination_params.get('pageSize')
        )
        #
        page = dict(
            hasNext=has_next,
            totalCount=count,
            currentPageSize=current_page_size,
            currentPageNumber=current_page_number,
            data=query.all())
        return page
