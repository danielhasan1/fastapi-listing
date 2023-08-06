from fastapi_listing.abstracts import AbsPaginatingStrategy
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest, ListingResponseType
from fastapi_listing.errors import ListingPaginatorError


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
        self.page_num = 0
        self.page_size = 0

    def get_count(self, query: SqlAlchemyQuery) -> int:
        """
        Override this method to return a dummy count or generate count in more optimized manner.
        User may want this to avoid slow count(*) query or double query or have page setup that doesn't require
        total_counts.
        Overall special checks needs to be setup.
        like returning a massive dummy count and then depending upon empty main_data avoiding trip to next page etc.
        """
        return query.count()

    def validate_params(self, page_num, page_size):
        """validate given 1 based page number and pagesize"""
        try:
            if isinstance(page_num, float) and not page_num.is_integer():
                raise ValueError
            if isinstance(page_size, float) and not page_size.is_integer():
                raise ValueError
            page_num, page_size = int(page_num), int(page_size)
        except (TypeError, ValueError):
            raise ListingPaginatorError("pagination params are not valid integers")
        if page_num < 1 or page_size < 1:
            raise ListingPaginatorError("page param(s) is less than 1")

    def set_page_num(self, page_num: int):
        self.page_num = page_num

    def set_page_size(self, page_size: int):
        self.page_size = page_size

    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict) -> ListingResponseType:
        page_num = pagination_params.get('page')
        page_size = pagination_params.get('pageSize')
        try:
            self.validate_params(page_num, page_size)
        except ListingPaginatorError:
            page_num = 1
            page_size = 10
        self.set_page_num(page_num)
        self.set_page_size(page_size)
        return self.page(query)

    def page(self, query: SqlAlchemyQuery) -> ListingResponseType:
        count: int = self.get_count(query)
        has_next = True if count - (self.page_num * self.page_size) > self.page_size else False
        query = self.slice_query(query)
        return ListingResponseType(
            hasNext=has_next,
            totalCount=count,
            currentPageSize=self.page_size,
            currentPageNumber=self.page_num,
            data=query.all())

    def slice_query(self, query: SqlAlchemyQuery):
        return query.limit(self.page_size).offset(max(self.page_num - 1, 0) * self.page_size)
