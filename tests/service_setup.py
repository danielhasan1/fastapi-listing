from fastapi_listing import ListingService, FastapiListing
from fastapi_listing.filters import generic_filters
from fastapi_listing.factory import strategy_factory
from fastapi_listing.strategies import QueryStrategy
from fastapi_listing.ctyping import FastapiRequest, SqlAlchemyQuery
from fastapi_listing.dao import dao_factory
from fastapi_listing import loader

from .pydantic_setup import EmployeeListDetails, EmployeeListDetailWithCustomFields
from .dao_setup import EmployeeDao, DeptEmpDao
from .dao_setup import Employee, Department, Title


class DepartmentEmployeesQueryStrategy(QueryStrategy):

    def get_query(self, *, request: FastapiRequest = None, dao: DeptEmpDao = None,
                  extra_context: dict = None) -> SqlAlchemyQuery:
        return dao.get_emp_dept_mapping_base_query()


class EmployeesQueryStrategy(QueryStrategy):

    def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                  extra_context: dict = None) -> SqlAlchemyQuery:
        return dao.get_employees_with_designations()


strategy_factory.register_strategy("dept_emp_mapping_query", DepartmentEmployeesQueryStrategy)
strategy_factory.register_strategy("titled_employees_query", EmployeesQueryStrategy)


@loader.register()
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
        "lnm": ("Employee.last_name", generic_filters.StringEndsWithFilter),
        "desg": ("Employee.Title.title", generic_filters.StringLikeFilter, lambda x: getattr(Title, x))
    }

    sort_mapper = {
        "cd": "emp_no"
    }
    default_srt_on = "Employee.emp_no"
    default_dao = EmployeeDao

    def get_listing(self):
        resp = {}
        if self.extra_context.get("q") == "vanilla":
            resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListDetails).get_response(self.MetaInfo(self))
        elif self.extra_context.get("q") == "custom_fields":
            resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListDetailWithCustomFields,
                                  custom_fields=True).get_response(
                self.MetaInfo(self))
        elif self.extra_context.get("q") == "titled_employees":
            self.switch("query_strategy", "titled_employees_query")
            resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListDetails).get_response(self.MetaInfo(self))
        elif self.extra_context.get("q") == "incorrect_switch":
            self.switch("sdfasd", "sdfsdf")
        return resp


class FullNameFilter(generic_filters.CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        # field is not necessary here as this is a custom filter and user have full control over its implementation
        if value:
            emp_dao: EmployeeDao = dao_factory.create("employee", replica=True)
            emp_ids: list[int] = emp_dao.get_emp_ids_contain_full_name(value.get("search"))
            query = query.filter(self.dao.model.emp_no.in_(emp_ids))  # noqa
        return query


@loader.register()
class DepartmentEmployeesListingService(ListingService):
    default_srt_on = "DeptEmp.emp_no"

    default_dao = DeptEmpDao
    query_strategy = "dept_emp_mapping_query"
    filter_mapper = {
        "flnm": ("DeptEmp.Employee.full_name", FullNameFilter),
        "gdr": ("DeptEmp.Employee.gender", generic_filters.EqualityFilter, lambda x: getattr(Employee, x)),
        "dptnm": (
            "DeptEmp.Department.dept_name", generic_filters.StringContainsFilter, lambda x: getattr(Department, x)),
        "hrdt": ("DeptEmp.Employee.hire_date", generic_filters.DataGreaterThanFilter, lambda x: getattr(Employee, x)),
        "tdt": ("DeptEmp.to_date", generic_filters.DataLessThanFilter),
        "tdt1": ("DeptEmp1.to_date", generic_filters.DataGreaterThanEqualToFilter),
        "tdt2": ("DeptEmp2.to_date", generic_filters.DataLessThanEqualToFilter),
        "lnm": ("DeptEmp.Employee.last_name", generic_filters.HasFieldValue, lambda x: getattr(Employee, x)),
        "gdr2": ("DeptEmp.Employee2.gender", generic_filters.InEqualityFilter, lambda x: getattr(Employee, x)),
        "empno": ("DeptEmp.emp_no", generic_filters.InDataFilter),
        "frmdt": ("DeptEmp.from_date", generic_filters.BetweenUnixMilliSecDateFilter)
    }
    sort_mapper = {
        "empno": ("Employee.emp_no", lambda x: getattr(Employee, x))
    }

    def get_listing(self):
        resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
        return resp


@loader.register()
class ErrorProneListingV1(ListingService):
    default_srt_on = "DeptEmp.emp_no"

    default_dao = DeptEmpDao

    sort_mapper = {
        "hdt": "Employee.hire_date"
    }

    def get_listing(self):
        return FastapiListing(self.request, self.dao, fields_to_fetch=["emp_no"]).get_response(self.MetaInfo(self))
