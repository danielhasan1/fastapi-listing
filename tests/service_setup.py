from fastapi_listing import ListingService, FastapiListing
from .pydantic_setup import EmployeeListDetails
from .dao_setup import EmployeeDao


class EmployeeListingService(ListingService):
    default_srt_on = "emp_no"
    default_dao = EmployeeDao

    def get_listing(self):
        resp = FastapiListing(self.request, self.dao, EmployeeListDetails).get_response(self.MetaInfo(self))
        return resp
