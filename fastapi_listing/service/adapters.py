from typing import Optional, List

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi import Request

from fastapi_listing import utils
from fastapi_listing.abstracts import AbstractListingFeatureParamsAdapter

__all__ = [
    "CoreListingParamsAdapter"
]


class CoreListingParamsAdapter(AbstractListingFeatureParamsAdapter):
    """Utilise this adapter class to make your remote client site:
    - filter,
    - sorter,
    - paginator.
    query params adapt to fastapi listing library.
    With this you can utilise same listing api to multiple remote client
    even if it's a front end server or other backend server.

    core service is always going to request one of the following fundamental key
    - sort
    - filter
    - pagination
    depending upon this return the appropriate transformed client param back to fastapi listing
    supported formats for
    filter:
    simple filter - [{"field":"<key used in filter mapper>", "value":{"search":"<client param>"}}, ...]
    if you are using a range filter -
    [{"field":"<key used in filter mapper>", "value":{"start":"<start range>", "end": "<end range>"}}, ...]
    if you are using a list filter i.e. search on given items
    [{"field":"<key used in filter mapper>", "value":{"list":["<client params>"]}}, ...]

    sort:
    [{"field":<"key used in sort mapper>", "type":"asc or "dsc"}, ...]
    by default single sort allowed you can change it by extending sort interceptor

    pagination:
    {"pageSize": <integer page size>, "page": <integer page number 1 based>}


    """
    def __init__(self, request: Optional[Request], extra_context):
        self.request = request
        self.extra_context = extra_context
        self.dependency = self.request.query_params if self.request else self.extra_context

    def get(self, key: Literal["sort", "filter", "pagination"]):
        """
        @param key: Literal["sort", "filter", "pagination"]
        @return: List[Optional[dict]] for filter/sort and dict for paginator
        """
        return utils.dictify_query_params(self.dependency.get(key))
