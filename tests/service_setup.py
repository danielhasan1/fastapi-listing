from fastapi_listing import ListingService, FastapiListing
from fastapi_listing.filters import generic_filters
from fastapi_listing.factory import filter_factory, strategy_factory
from fastapi_listing.strategies import QueryStrategy
from fastapi_listing.ctyping import FastapiRequest, SqlAlchemyQuery
from fastapi_listing.dao import dao_factory

from .pydantic_setup import EmployeeListDetails, EmployeeListDetailWithCustomFields
from .dao_setup import EmployeeDao, DeptEmpDao


class EmployeeListingService(ListingService):
    """
    Testing vanilla flow,
    filters,
    default query generation,
    default flow,
    custom_fields,
    """
    filter_mapper = {
        "gdr": ("Employee.gender", generic_filters.EqualityFilter),
        "bdt": ("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter),
        "fnm": ("Employee.first_name", generic_filters.StringStartsWithFilter),
        "lnm": ("Employee.last_name", generic_filters.StringEndsWithFilter)
    }

    sort_mapper = {
        "cd": "emp_no"
    }
    default_srt_on = "emp_no"
    default_dao = EmployeeDao

    def get_listing(self):
        resp = {}
        if self.extra_context.get("q") == "vanilla":
            resp = FastapiListing(self.request, self.dao, EmployeeListDetails).get_response(self.MetaInfo(self))
        elif self.extra_context.get("q") == "custom_fields":
            resp = FastapiListing(self.request, self.dao, EmployeeListDetailWithCustomFields,
                                  custom_fields=True).get_response(
                self.MetaInfo(self))
        return resp


filter_factory.register_filter_mapper(EmployeeListingService.filter_mapper)


class FullNameFilter(generic_filters.CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        # field is not necessary here as this is a custom filter and user have full control over its implementation
        if value:
            emp_dao: EmployeeDao = dao_factory.create("employee", replica=True)
            emp_ids: list[int] = emp_dao.get_emp_ids_contain_full_name(value.get("search"))
            query = query.filter(self.dao.model.emp_no.in_(emp_ids))  # noqa
        return query


class DepartmentEmployeesListingService(ListingService):

    default_srt_on = "emp_no"
    default_dao = DeptEmpDao
    query_strategy = "dept_emp_mapping_query"
    filter_mapper = {
        "flnm": ("DeptEmp.Employee.full_name", FullNameFilter)
    }

    def get_listing(self):
        resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
        return resp


filter_factory.register_filter_mapper(DepartmentEmployeesListingService.filter_mapper)


class DepartmentEmployeesQueryStrategy(QueryStrategy):

    def get_query(self, *, request: FastapiRequest = None, dao: DeptEmpDao = None,
                  extra_context: dict = None) -> SqlAlchemyQuery:
        return dao.get_emp_dept_mapping_base_query()


strategy_factory.register_strategy("dept_emp_mapping_query", DepartmentEmployeesQueryStrategy)
