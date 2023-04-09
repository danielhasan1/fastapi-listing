from fastapi_listing.factory import filter_factory, generic_factory
from fastapi_listing.filters import CommonFilterImpl


class FilterMechanics:

    def apply(self, *, query, filter_params: list[dict[str, str]], dao, request):
        for applied_filter in filter_params:
            filter_obj: CommonFilterImpl = filter_factory.create(applied_filter.get("field"),
                                                                 dao=dao,
                                                                 request=request)
            query = filter_obj.filter(field=applied_filter.get("field"),
                                      value=applied_filter.get("value"),
                                      query=query)
        return query


def register() -> None:
    generic_factory.register("filter_mechanics", FilterMechanics)