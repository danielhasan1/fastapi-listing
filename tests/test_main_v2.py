import json
from typing import Union

from fastapi import Request, Query
from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_listing.middlewares import DaoSessionBinderMiddleware
from .dao_setup import register

from .service_setup import (
    EmployeeListingService,
    DepartmentEmployeesListingService,
    ErrorProneListingV1,
)

from .pydantic_setup import (
    EmployeeListingResponse,
    EmployeeListingResponseWithCustomFields,
    DepartMentEmployeeListingResp,
    TitledEmployeeListingResp,
    EmployeeListDetails,
    EmployeeListDetailWithCustomFields,
    DepartMentEmployeeListingDetails,
    TitledEmployeeListingDetails
)

from . import original_responses

from urllib.parse import quote

from fastapi_listing.paginator import ListingPage
# register all models with dao


register()


def get_db() -> Session:
    """
    replicating sessionmaker for any fastapi app.
    anyone could be using a different way or opensource packages like fastapi-sqlalchemy
    it all comes down to a single result that is yielding a session.
    for the sake of simplicity and testing purpose I'm replicating this behaviour in this naive way.
    :return: Session
    """
    engine = create_engine("mysql://root:123456@127.0.0.1:3307/employees", pool_pre_ping=1)
    sess = Session(bind=engine)
    return sess


app = FastAPI()
# fastapi-listing middleware offering anywhere dao usage policy.
app.add_middleware(DaoSessionBinderMiddleware, master=get_db, )


def get_url_quoted_string(d):
    return quote(json.dumps(d))


# test routers starts here


@app.get("/v1/employees", response_model=ListingPage[EmployeeListDetails])
def read_main(request: Request, q: str = Query("vanilla", alias="q")):
    resp = EmployeeListingService(request,
                                  q=q).get_listing()
    return resp


@app.get("/v1/custom-employees", response_model=ListingPage[EmployeeListDetailWithCustomFields])
def read_main_with_custom_field(request: Request, q: str = Query("custom-fields", alias="q")):
    resp = EmployeeListingService(request,
                                  q=q).get_listing()
    return resp


@app.get("/v1/titles-employees", response_model=ListingPage[TitledEmployeeListingDetails])
def read_titled_employees(request: Request, q: str = Query("titled_employees", alias="q")):
    resp = EmployeeListingService(request,
                                  q=q).get_listing()
    return resp


@app.get("/v1/dep-emp", response_model=ListingPage[DepartMentEmployeeListingDetails])
def read_dep_emp_mapping(request: Request):
    resp = DepartmentEmployeesListingService(request).get_listing()
    return resp


@app.get("/v1/error-sorting")
def error_sorting(request: Request):
    return ErrorProneListingV1(request).get_listing()


# @app.get("/v1/errorprone-listing")
# def error_prone_listing(request: Request):
#     return ErrorProneListingV2(request).get_listing()


client = TestClient(app)


def test_default_employee_listing():
    response = client.get("/v1/employees")
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing


def test_default_employee_listing_filter():
    # equality filter
    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "gdr", "value": {"search": "M"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_gender_filter

    # native date filter
    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "bdt", "value": {"start": "1958-05-01",
                                                                                              "end": "1958-05-01"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )

    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_birth_date_filter

    # starts with filter
    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "fnm", "value": {"search": "Sach"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_first_name_filter

    # ends with filter
    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "lnm", "value": {"search": "kuda"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_last_name_filter

    # like filter
    response = client.get("/v1/titles-employees",
                          params={"filter": get_url_quoted_string([{"field": "desg", "value": {"search": "Engineer"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_string_like_filter


def test_custom_serializer_field():
    # Best flow suppresses custom field error
    response = client.get("/v1/custom-employees?q=custom_fields",
                          params={"filter": get_url_quoted_string([{"field": "lnm", "value": {"search": "kuda"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_employee_listing_with_custom_field


def test_sorting_on_default_listing():
    response = client.get("/v1/employees", params={
        "sort": get_url_quoted_string([{"field": "cd", "type": "asc"}])
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_asc_sorted


def test_dept_emp_mapping_listing():
    response = client.get("/v1/dep-emp", params={
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_dept_emp_mapping_page_resp


def test_dept_emp_mapping_listing_with_filters():
    # custom filter
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "flnm", "value": {"search": "Sumant P"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_dept_emp_mapping_full_name_filter_resp

    # equality filter with custom extractor
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "gdr", "value": {"search": "M"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_custom_field_extractor

    # string contains filter
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "dptnm", "value": {"search": "ales"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_string_contains_filter

    # greater than filter
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "hrdt", "value": {"search": "2000-01-23"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_greater_than_filter

    # less than filter
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "tdt", "value": {"search": "1985-03-01"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_less_than_filter

    # greater than equal to
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "tdt1", "value": {"search": "9999-01-01"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_greater_than_equal_to_filter

    # less than equal to
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "tdt2", "value": {"search": "1985-02-17"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_less_than_filter

    # has last_name
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "lnm", "value": {"search": True}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_has_field_value_filter

    # not has last_name
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "lnm", "value": {"search": False}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_has_none_value_filter

    # inequality
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "gdr2", "value": {"search": "M"}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_inequality_filter

    # in data
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "empno", "value": {"list": [499995, 11538]}}]),
        "pagination": get_url_quoted_string({"pageSize": 10, "page": 1})
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_indata_filter

    # unixbetwen
    response = client.get("/v1/dep-emp", params={
        "filter": get_url_quoted_string([{"field": "frmdt", "value": {"start": 1689356654000,
                                                                      "end": 1689356709000}}]),
        "pagination": get_url_quoted_string({"pageSize": 1, "page": 1}),
        "sort": get_url_quoted_string([{"field": "empno", "type": "asc"}])
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_unix_between_filter


def test_incorrect_type_switch():
    with pytest.raises(ValueError) as e:
        client.get("/v1/employees?q=incorrect_switch")
    assert e.value.args[0] == "unknown strategy type!"


def test_sorting_error():
    with pytest.raises(ValueError) as e:
        client.get("/v1/error-sorting",
                   params={"sort": get_url_quoted_string([{"field": "hdt", "type": "asc"}])})
    assert e.value.args[0] == "Provided sort field 'hire_date' is not an attribute of DeptEmp"


def test_core_service_exceptions():
    resp = client.get("/v1/error-sorting",
                      params={"sort": '%5B%22field%22%3A%20%22hdt%22%2C%20%22type%22%22asc%22%7D%5D'})
    assert resp.status_code == 422
    assert resp.json() == {'detail': 'Crap! Sorting went wrong.'}

    resp = client.get("/v1/error-sorting",
                      params={"sort": get_url_quoted_string([{"field": "hdtds", "type": "asc"}])})

    assert resp.status_code == 409
    assert resp.json() == {'detail': "Sorter(s) not registered with listing: {'hdtds'}, Did you forget to do it?"}

    resp = client.get("/v1/error-sorting",
                      params={"filter": get_url_quoted_string([{"field": "hdtds", "type": "asc"}])})
    assert resp.status_code == 409
    assert resp.json() == {'detail': "Filter(s) not registered with listing: {'hdtds'}, Did you forget to do it?"}
    resp = client.get("/v1/error-sorting",
                      params={"filter": '%5B%22field%22%3A%20%22hdt%22%2C%20%22type%22%22asc%22%7D%5D'})

    assert resp.status_code == 422
    assert resp.json() == {'detail': 'Crap! Filtering went wrong.'}

    resp = client.get("/v1/error-sorting",
                      params={"pagination": '%5B%22field%22%3A%20%22hdt%22%2C%20%22type%22%22asc%22%7D%5D'})

    assert resp.status_code == 422
    assert resp.json() == {'detail': 'Crap! Pagination went wrong.'}


def test_loader():
    from fastapi_listing.errors import MissingExpectedAttribute
    from fastapi_listing import loader, ListingService
    with pytest.raises(MissingExpectedAttribute) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = ""

    assert e.value.args[0] == "default_srt_on attribute value is not provided! Did you forget to do it?"
    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            query_strategy = "dont know"

    assert e.value.args[0] == \
           "ErrorProneListingV2 attribute 'dont know' is not registered/loaded! Did you forget to do it?"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            sorting_strategy = "dont know"

    assert e.value.args[0] == \
           "ErrorProneListingV2 attribute 'dont know' is not registered/loaded! Did you forget to do it?"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            paginate_strategy = "dont know"

    assert e.value.args[0] == \
           "ErrorProneListingV2 attribute 'dont know' is not registered/loaded! Did you forget to do it?"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            filter_mecha = "dont know"

    assert e.value.args[0] == \
           "ErrorProneListingV2 attribute 'dont know' is not registered/loaded! Did you forget to do it?"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            sort_mecha = "dont know"

    assert e.value.args[0] == \
           "ErrorProneListingV2 attribute 'dont know' is not registered/loaded! Did you forget to do it?"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"

    assert e.value.args[0] == "Avoid using GenericDao Directly! Extend it!"

    with pytest.raises(TypeError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            default_dao = ListingService

    assert e.value.args[0] == "Invalid Dao Type! Should Be type of GenericDao"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            default_dao = "dfs"

    assert e.value.args[0] == "Invalid Dao reference Injected!"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            feature_params_adapter = ""
            default_dao = EmployeeListingService.default_dao

    assert e.value.args[0] == "Missing Adapter class for client param conversion!"

    with pytest.raises(TypeError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            query_strategy = EmployeeListingService.default_dao

    assert e.value.args[0] == "ErrorProneListingV2 has invalid type attribute! Please refer to docs!"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            default_page_size = EmployeeListingService.default_dao

    assert e.value.args[0] == "ErrorProneListingV2 has invalid default_page_size attribute!"

    with pytest.raises(ValueError) as e:
        @loader.register()
        class ErrorProneListingV2(ListingService):  # noqa: F811,F841
            default_srt_on = "sdfasd"
            default_srt_ord = ""

    assert e.value.args[0] == "Missing default_srt_ord attribute!"
