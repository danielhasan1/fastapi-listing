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
)

from .pydantic_setup import (
    EmployeeListingResponse,
    EmployeeListingResponseWithCustomFields
)

from . import original_responses

from urllib.parse import quote

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
    engine = create_engine("mysql://root:123456@127.0.0.1:3306/employees", pool_pre_ping=1)
    sess = Session(bind=engine)
    return sess


app = FastAPI()
# fastapi-listing middleware offering anywhere dao usage policy.
app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)


def get_url_quoted_string(d):
    return quote(json.dumps(d))


# test routers starts here


@app.get("/v1/employees", response_model=Union[EmployeeListingResponse,])
def read_main(request: Request, q: str = Query("vanilla", alias="q")):
    resp = EmployeeListingService(request,
                                  q=q).get_listing()
    return resp


@app.get("/v1/custom-employees", response_model=Union[EmployeeListingResponseWithCustomFields,])
def read_main_with_custom_field(request: Request, q: str = Query("custom-fields", alias="q")):
    resp = EmployeeListingService(request,
                                  q=q).get_listing()
    return resp


client = TestClient(app)


def test_default_employee_listing():
    response = client.get("/v1/employees")
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing


def test_default_employee_listing_filter():
    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "gdr", "value": {"search": "M"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_gender_filter

    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "bdt", "value": {"start": "1958-05-01",
                                                                                              "end": "1958-05-01"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )

    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_birth_date_filter

    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "fnm", "value": {"search": "Sach"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_first_name_filter

    response = client.get("/v1/employees",
                          params={"filter": get_url_quoted_string([{"field": "lnm", "value": {"search": "kuda"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_last_name_filter


def test_custom_serializer_field():
    # Best flow suppresses custom field error
    response = client.get("/v1/custom-employees?q=custom_fields",
                          params={"filter": get_url_quoted_string([{"field": "lnm", "value": {"search": "kuda"}}]),
                                  "pagination": get_url_quoted_string({"pageSize": 1, "page": 1})
                                  }
                          )
    assert response.status_code == 200
    assert response.json() == original_responses.test_employee_listing_with_custom_field

import logging

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=r"C:\Users\danis\dev\test.log", mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)
def test_sorting_on_default_listing():
    response = client.get("/v1/employees", params={
        "sort": get_url_quoted_string([{"field":"cd", "type":"asc"}])
    })
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_asc_sorted

