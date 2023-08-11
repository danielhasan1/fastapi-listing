from fastapi_listing import utils
from fastapi_listing.abstracts import AbstractListingFeatureParamsAdapter


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
    for digest and return back your desired result set.
    """
    def __init__(self, request):
        self.request = request

    def get(self, key: str):
        return utils.dictify_query_params(self.request.query_params.get(key))
