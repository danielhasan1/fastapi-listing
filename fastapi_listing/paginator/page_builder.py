from fastapi_listing.abstracts import AbsPaginatingStrategy
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest


class PaginationStrategy(AbsPaginatingStrategy):
    """
    Loosely coupled paginator module.
    """
    NAME = "default_paginator"

    def __init__(self, request: FastapiRequest):
        self.request = request

    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict):
        count = query.count()
        has_next = True if count - ((pagination_params.get('page')) * pagination_params.get('page_size')
                                    ) > pagination_params.get('page_size') else False
        current_page_size = pagination_params.get("page_size")
        current_page_number = pagination_params.get("page")
        query = query.limit(
            pagination_params.get('page_size')
        ).offset(
            (pagination_params.get('page')) * pagination_params.get('page_size')
        )
        #
        page = dict(
            page_meta_data=dict(
                has_next=has_next,
                total_count=count,
                current_page_size=current_page_size,
                current_page_number=current_page_number,
            ),
            main_data=query.all())
        return page
