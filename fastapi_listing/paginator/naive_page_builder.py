from fastapi_listing import utils
from fastapi_listing.abstracts import TableDataPaginatingStrategy


class NaivePaginationStrategy(TableDataPaginatingStrategy):

    default_pagination_params = {"pageSize": 10, "page": 0}
    DEFAULT_PAGE_TEMPLATE = {"data": None, "hasNext": None, "totalCount": None,
                             "currentPageSize": None, "currentPageNumber": None}

    def paginate(self, query, request):
        pagination_params = self.default_pagination_params
        pagination_params = utils.jsonify_query_params(request.query_params.get('pagination')) \
            if request.query_params.get('pagination') else pagination_params
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
