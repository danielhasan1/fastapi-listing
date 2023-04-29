from json import JSONDecodeError
from fastapi_listing import utils
from fastapi_listing.abstracts import TableDataPaginatingStrategy
from fastapi_listing.errors import ListingPaginatorError
from fastapi_listing.typing import SqlAlchemyQuery, FastapiRequest


class NaivePaginationStrategy(TableDataPaginatingStrategy):
    """
    Loosely coupled paginator module.
    """

    default_pagination_params = {"pageSize": 10, "page": 0}
    PAGE_TEMPLATE = {"data": None, "hasNext": None, "totalCount": None,
                     "currentPageSize": None, "currentPageNumber": None}

    def paginate(self, query: SqlAlchemyQuery, request: FastapiRequest, extra_context: dict):
        pagination_params = self.default_pagination_params
        try:
            pagination_params = utils.jsonify_query_params(request.query_params.get('pagination')) \
                if request.query_params.get('pagination') else pagination_params
        except JSONDecodeError:
            raise ListingPaginatorError("pagination params are not valid json!")
        count = query.count()
        has_next = True if count - ((pagination_params.get('page')) * pagination_params.get('pageSize')) > \
                           pagination_params.get('pageSize') else False
        current_page_size = pagination_params.get("pageSize")
        current_page_number = pagination_params.get("page")
        query = query.limit(
            pagination_params.get('pageSize')
        ).offset(
            (pagination_params.get('page')) * pagination_params.get('pageSize')
        )
        page = dict(data=query.all(), hasNext=has_next, totalCount=count, currentPageSize=current_page_size,
                    currentPageNumber=current_page_number)
        return page
