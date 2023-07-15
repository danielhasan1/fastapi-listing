from fastapi_listing import utils


class CoreListingParamsAdapter:

    def __init__(self, request):
        self.request = request

    def get(self, key: str):
        print(self.request.query_params.get(key), key)
        return utils.dictify_query_params(self.request.query_params.get(key))
