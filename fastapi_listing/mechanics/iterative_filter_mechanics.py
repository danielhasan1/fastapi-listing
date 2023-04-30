from fastapi_listing.factory import filter_factory, _generic_factory
from fastapi_listing.filters import CommonFilterImpl
from fastapi_listing.typing import SqlAlchemyQuery, FastapiRequest


class IterativeFilterMechanics:

    """
    Iterative Filter Applicator.
    Applies all client site filter in iterative manner.
    one by one call is made to registered filters and each filterd query is returned.

    User can write their own applicator if they don't want iterative applicator
    or have more complex way to apply filter like
    if one filter is applied then don't apply the other one vice versa.
    to give a real world example
    if user has applied city, pincode, region filter then
    pincode is the most atomic unit here region and city filters are just extra burden on query and db as well.
    one can tackle this situation by having a mechanic which will check if specific filter is applied
    with other relative filters then don't apply other relative filters...
    """

    def apply(self, *, query: SqlAlchemyQuery = None, filter_params: list[dict[str, str]], dao=None,
              request: FastapiRequest = None, extra_context: dict = None) -> SqlAlchemyQuery:
        for applied_filter in filter_params:
            filter_obj: CommonFilterImpl = filter_factory.create(applied_filter.get("field"),
                                                                 dao=dao,
                                                                 request=request,
                                                                 extra_context=extra_context)
            query = filter_obj.filter(field=applied_filter.get("field"),
                                      value=applied_filter.get("value"),
                                      query=query)
        return query


# def register() -> None:
#     generic_factory.
