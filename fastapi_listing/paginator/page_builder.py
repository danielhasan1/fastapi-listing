from fastapi_listing.abstracts import AbsPaginatingStrategy
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest, Page, BasePage
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
        self.extra_context = None

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

    def set_extra_context(self, extra_context):
        self.extra_context = extra_context

    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict) -> BasePage:
        page_num = pagination_params.get('page')
        page_size = pagination_params.get('pageSize')
        try:
            self.validate_params(page_num, page_size)
        except ListingPaginatorError:
            page_num = 1
            page_size = 10
        self.set_page_num(page_num)
        self.set_page_size(page_size)
        self.set_extra_context(extra_context)
        return self.page(query)

    def page(self, query: SqlAlchemyQuery) -> BasePage:
        """Return a Page or extended BasePage for given 1-based page number."""
        count: int = self.get_count(query)
        has_next = True if count - (self.page_num * self.page_size) > self.page_size else False
        query = self._slice_query(query)
        return self._get_page(count, has_next, query)

    def _get_page(self, *args, **kwargs) -> Page:
        """
        Return a single page of items
        this hook can be used by subclasses if you want to
        replace Page datastructure with your custom structure extending BasePage.
        """
        total_count, has_next, query = args
        return Page(
            hasNext=has_next,
            totalCount=total_count,
            currentPageSize=self.page_size,
            currentPageNumber=self.page_num,
            data=query.all())

    def _slice_query(self, query: SqlAlchemyQuery) -> SqlAlchemyQuery:
        """
        Return sliced query.

        This hook can be used by subclasses to slice query in a different manner
        like using an id range with the help of shared extra_contex
        or using a more advanced offset technique.
        """
        return query.limit(self.page_size).offset(max(self.page_num - 1, 0) * self.page_size)
