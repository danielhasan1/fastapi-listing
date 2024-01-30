from typing import Optional, Union

from fastapi_listing.abstracts import AbsPaginatingStrategy
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest, Page, BasePage, PageWithoutCount
from fastapi_listing.errors import ListingPaginatorError


class PaginationStrategy(AbsPaginatingStrategy):
    """
    Loosely coupled paginator module.
    Type of page should always be maintained for core service to make sense of a page for any post page
    spawn processing.
    Clients are advised to use any adapter in their listing service for refactoring page response as per
    their needs or having a different response structure.
    """

    def __init__(self, request: Optional[FastapiRequest] = None, fire_count_qry: bool = True):
        self.request = request
        self.page_num = 0
        self.page_size = 0
        self.count = 0
        self.extra_context = None
        self.fire_count_qry = fire_count_qry

    def get_count(self, query: SqlAlchemyQuery) -> int:
        """
        Override this method to return a dummy count or generate count in more optimized manner.
        User may want this to avoid slow count(*) query or double query or have page setup that doesn't require
        total_counts.
        Overall special checks needs to be setup.
        like returning a massive dummy count and then depending upon empty main_data avoiding trip to next page etc.
        """
        return query.count()

    def is_next_page_exists(self) -> bool:
        """expression results in bool val if count query allowed else None"""
        if self.fire_count_qry:
            return True if self.count - (self.page_num * self.page_size) > self.page_size else False
        else:
            return self.count > self.page_size

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

    def set_count(self, count: int):
        self.count = count

    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict) -> BasePage:
        """Return paginated response"""
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
        """Return a Page or BasePage for given 1-based page number."""
        if self.fire_count_qry:
            self.set_count(self.get_count(query))
            has_next: bool = self.is_next_page_exists()
            query = self._slice_query(query)
            return self._get_page(has_next, query)
        else:
            query = self._slice_query(query)
            return self._get_page_without_count(query)

    def _get_page(self, *args, **kwargs) -> Page:
        """
        Return a single page of items
        this hook can be used by subclasses if you want to
        replace Page datastructure with your custom structure extending BasePage.
        """
        has_next, query = args
        total_count = self.count
        return Page(
            hasNext=has_next,
            totalCount=total_count,
            currentPageSize=self.page_size,
            currentPageNumber=self.page_num,
            data=query.all())

    def _get_page_without_count(self, *args, **kwargs) -> PageWithoutCount:
        """Get Page without total count for avoiding slow count query"""
        query = args[0]
        data = query.all()
        self.set_count(len(data))
        has_next = self.is_next_page_exists()
        return PageWithoutCount(
            hasNext=has_next,
            currentPageSize=self.page_size,
            currentPageNumber=self.page_num,
            data=data[: self.count - 1] if has_next else data
        )


    def _slice_query(self, query: SqlAlchemyQuery) -> SqlAlchemyQuery:
        """
        Return sliced query.

        This hook can be used by subclasses to slice query in a different manner
        like using an id range with the help of shared extra_contex
        or using a more advanced offset technique.
        """
        if self.fire_count_qry:
            return query.limit(self.page_size).offset(max(self.page_num - 1, 0) * self.page_size)
        else:
            # get +1 than page size to see if next page exists
            # a hotfix to avoid total count to determine next page existence
            return query.limit(self.page_size + 1).offset(max(self.page_num - 1, 0) * self.page_size)
