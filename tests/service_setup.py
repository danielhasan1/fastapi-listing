from fastapi_listing import ListingService, FastapiListing
from fastapi_listing.filters import generic_filters
from fastapi_listing.factory import filter_factory

from .pydantic_setup import EmployeeListDetails, EmployeeListDetailWithCustomFields
from .dao_setup import EmployeeDao


filter_factory.register_filter("Employee.gender", generic_filters.EqualityFilter)
filter_factory.register_filter("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter)
filter_factory.register_filter("Employee.first_name", generic_filters.StringStartsWithFilter)
filter_factory.register_filter("Employee.last_name", generic_filters.StringEndsWithFilter)


class EmployeeListingService(ListingService):
    """
    Testing vanilla flow,
    filters,
    default query generation,
    default flow,
    custom_fields,
    """
    filter_mapper = {
        "gdr": "Employee.gender",
        "bdt": "Employee.birth_date",
        "fnm": "Employee.first_name",
        "lnm": "Employee.last_name"
    }
    default_srt_on = "emp_no"
    default_dao = EmployeeDao

    def get_listing(self):
        if self.extra_context.get("q") == "vanilla":
            resp = FastapiListing(self.request, self.dao, EmployeeListDetails).get_response(self.MetaInfo(self))
        elif self.extra_context.get("q") == "custom_fields":
            resp = FastapiListing(self.request, self.dao, EmployeeListDetailWithCustomFields,
                                  custom_fields=True).get_response(
                self.MetaInfo(self))
        else:
            resp = {}

        return resp
