from fastapi import Request
from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient
from .fake_listing_setup import ProductPage, TestListingServiceDefaultFlow, fake_db_response, \
    fake_db_response_page_size_1, TestListinghServiceVariablePageFlow, TestListingServiceSortFlow, \
    spawn_valueerror_for_strategy_registry, spawn_valueerror_for_filter_factory, invalid_type_factory_keys
from fastapi_listing.errors import ListingFilterError

app = FastAPI()


@app.get("/", response_model=ProductPage)
def read_main(request: Request):
    resp = TestListingServiceDefaultFlow(request, read_db="read_db_session", write_db="write_db_session").get_listing()
    return resp


@app.get("/var-page", response_model=ProductPage)
def read_limit_1_page(request: Request):
    resp = TestListinghServiceVariablePageFlow(request, read_db="read_db_session",
                                               write_db="write_db_session").get_listing()
    return resp


@app.get("/sort", response_model=ProductPage)
def sort_test(reqeust: Request):
    resp = TestListingServiceSortFlow(reqeust).get_listing()
    return resp


client = TestClient(app)


def test_call_default():
    response = client.get("/", params={"pagination": "%7B%22pageSize%22%3A10%2C%20%22page%22%3A0%7D"})
    assert response.status_code == 200
    assert response.json() == fake_db_response


def test_call_variable_page():
    response = client.get("/var-page", params={"pagination": "%7B%22pageSize%22%3A1%2C%20%22page%22%3A0%7D"})
    assert response.status_code == 200
    assert response.json() == fake_db_response_page_size_1


def test_call_filter_not_registered():
    # filter = [{"field":"abc", "value":{"search":"something"}}]
    # with pytest.raises(Exception) as exc_info:
    response = client.get("/var-page", params={"pagination": "%7B%22pageSize%22%3A1%2C%20%22page%22%3A0%7D",
                                               "filter": "%5B%7B%22field%22%3A%22abc%22%2C%20%22value%22%3A%7B%22search%22%3A%22something%22%7D%7D%5D"})

    assert response.status_code == 409
    assert response.json().get("detail") == "Filter'(s) not registered with listing: {'abc'}, Did you forget to do it?"


def test_call_sort_not_registered():
    # sort =[{"field":"abc", "type":"asc"}]
    response = client.get("/var-page", params={"pagination": "%7B%22pageSize%22%3A1%2C%20%22page%22%3A0%7D",
                                               "sort": "%5B%7B%22field%22%3A%22abc%22%2C%20%22type%22%3A%22asc%22%7D%5D"})

    assert response.status_code == 409
    assert response.json().get("detail") == "Sorter'(s) not registered with listing: {'abc'}, Did you forget to do it?"


def test_defective_sorter_semantic():
    response = client.get("/var-page", params={"pagination": "%7B%22pageSize%22%3A1%2C%20%22page%22%3A0%7D",
                                               "sort": "%5B%7B%22field%22%3Aabc%22%2C%20%22type%22%22asc%22%7D%5D"})

    assert response.status_code == 422
    assert response.json().get("detail") == "sorter param is not a valid json!"


def test_defective_filter_semantic():
    response = client.get("/var-page", params={"pagination": "%7B%22pageSize%22%3A1%2C%20%22page%22%3A0%7D",
                                               "filter": "%5B%7B%22field%22%3A%22abc%22%2C%20%22value%22%7B%22searsomething%22%7D%5D"})

    assert response.status_code == 422
    assert response.json().get("detail") == "filter param is not a valid json!"


def test_unknown_sorting_style():
    with pytest.raises(AssertionError) as e:
        response = client.get("/sort", params={"pagination": "%7B%22pageSize%22%3A1%2C%20%22page%22%3A0%7D",
                                               "sort": "%5B%7B%22field%22%3A%22id%22%2C%20%22type%22%3A%22somethingse%22%7D%5D"})

    assert e.value.args[0] == "invalid sorting style!"


def test_strategy_factory_unique_strategy_register():
    with pytest.raises(ValueError) as e:
        spawn_valueerror_for_strategy_registry("same_strategy_key", "same_strategy_key")
    assert e.value.args[0] == "strategy name already in use with FakePaginationStrategyV2!"


def test_filter_factory_unique_strategy_register():
    with pytest.raises(ValueError) as e:
        spawn_valueerror_for_filter_factory("same_field_name", "same_field_name")
    assert e.value.args[0] == "filter name already in use with EqualityFilter!"


def test_factory_key_inputs():
    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("filter", None)
    assert e.value.args[0] == "Invalid type key!"

    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("filter", "")
    assert e.value.args[0] == "Invalid type key!"

    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("strategy", None)
    assert e.value.args[0] == "Invalid type key!"

    with pytest.raises(ValueError) as e:
        invalid_type_factory_keys("strategy", "")
    assert e.value.args[0] == "Invalid type key!"
