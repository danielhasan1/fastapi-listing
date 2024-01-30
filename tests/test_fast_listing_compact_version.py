import json
from urllib.parse import quote
from typing import Union

from fastapi import Request, Query
from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_listing import FastapiListing, MetaInfo
from fastapi_listing.paginator import ListingPage, ListingPageWithoutCount

from tests.pydantic_setup import EmployeeListDetails
from tests.dao_setup import EmployeeDao
from tests import original_responses


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


def get_url_quoted_string(d):
    return quote(json.dumps(d))


@app.get("/v1/employees", response_model=ListingPage[EmployeeListDetails])
def read_main(request: Request):
    dao = EmployeeDao(read_db=get_db())
    resp = FastapiListing(dao=dao,
                          pydantic_serializer=EmployeeListDetails).get_response(MetaInfo(default_srt_on="emp_no"))
    return resp


@app.get("/v1/without-count/employees", response_model=ListingPageWithoutCount[EmployeeListDetails])
def read_main(request: Request):
    dao = EmployeeDao(read_db=get_db())
    resp = FastapiListing(dao=dao,
                          pydantic_serializer=EmployeeListDetails
                          ).get_response(MetaInfo(default_srt_on="emp_no", allow_count_query_by_paginator=False))
    return resp


client = TestClient(app)


def test_default_employee_listing():
    response = client.get("/v1/employees")
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing


def test_listing_without_total_count():
    response = client.get("/v1/without-count/employees")
    assert response.status_code == 200
    assert response.json() == original_responses.test_default_employee_listing_without_count
