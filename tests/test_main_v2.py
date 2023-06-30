from fastapi import Request
from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_listing.middlewares import DaoSessionBinderMiddleware
from .dao_setup import register

from .service_setup import \
    EmployeeListingService

from .pydantic_setup import \
    EmployeeListingResponse

from . import original_responses

# register all models with dao


register()

import logging
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=r"C:\Users\danis\Desktop\fastapi-listing\tests\test.log", mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)


def get_db() -> Session:
    """
    replicating sessionmaker for any fastapi app.
    anyone could be using a different way or opensource packages like fastapi-sqlalchemy
    it all comes down to a single result that is yielding a session.
    for the sake of simplicity and testing purpose I'm replicating this behaviour in this naive way.
    :return: Session
    """
    engine = create_engine("mysql://root:123456@localhost:3306/employees", pool_pre_ping=1)
    sess = Session(bind=engine)
    return sess


app = FastAPI()
# fastapi-listing middleware offering anywhere dao usage policy.
app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)

# test routers starts here


@app.get("/v1/employees", response_model=EmployeeListingResponse)
def read_main(request: Request):
    resp = EmployeeListingService(request).get_listing()
    return resp


client = TestClient(app)


def test_default_employee_listing():
    response = client.get("/v1/employees")
    assert response.status_code == 200
    logger.info(f"{response.json()}")
    assert response.json() == original_responses.test_default_employee_listing

