from fastapi_listing import utils
from fastapi_listing.abstracts import TableDataSortingStrategy


class SortingOrderStrategy(TableDataSortingStrategy):

    identifier = None

    def __init__(self, field):
        self.default_sort_on = field

    def sort(self, *, query=None, request=None, model=None, field_mapper=None):
        raise NotImplementedError

    def get_request_sorting_param(self, request, field_mapper) -> str:
        sorting_param = utils.jsonify_query_params(request.query_params.get("sort"))
        if not sorting_param:
            return ""
        sorting_param = sorting_param[0].get("field")
        if sorting_param not in field_mapper:
            raise ValueError # todo improve this by custom exception
            # raise CashifyApiException(LogisticsException.SORT_NOT_REGISTERED, LogisticsDiagnoCode.PLG1014)
        return field_mapper.get(sorting_param)

    @staticmethod
    def validate_srt_field(model, sort_field):
        try:
            inst_field = getattr(model, sort_field)
        except AttributeError:
            inst_field = None
        if not inst_field:
            raise ValueError  # todo improve this by custom exception
            # raise CashifyApiException(LogisticsException.INVALID_SORT_FIELD, LogisticsDiagnoCode.PLG1013)
        return inst_field


class AscendingOrderSortingStrategy(SortingOrderStrategy):
    """
        Strictly works on table fields.
    """

    identifier = "asc"

    def sort(self, *, query=None, request=None, model=None, field_mapper=None):
        req_param = self.get_request_sorting_param(request, field_mapper)
        sort_on = req_param or self.default_sort_on
        inst_field = self.validate_srt_field(model, sort_on)
        query = query.order_by(inst_field.asc())
        return query


class DescendingOrderSortingStrategy(SortingOrderStrategy):
    """
    Strictly works on table fields.
    """

    identifier = "dsc"

    def sort(self, *, query=None, request=None, model=None, field_mapper=None):
        req_param = self.get_request_sorting_param(request, field_mapper)
        sort_on = req_param or self.default_sort_on
        inst_field = self.validate_srt_field(model, sort_on)
        query = query.order_by(inst_field.desc())
        return query
