from fastapi_listing import FastapiListing, ListingService
from fastapi_listing.strategies import NaiveQueryStrategy, NaivePaginationStrategy, SortingOrderStrategy
from fastapi_listing.factory import strategy_factory, filter_factory
from fastapi_listing.filters import generic_filters
from fastapi_listing.dao import GenericDao
from pydantic import BaseModel, Field
from fastapi_listing import utils
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import BIT
from typing import List, Dict

Base = declarative_base()

fake_db = [
    {
        "id": 1,
        "product_name": "Hyundai Verna",
        "is_active": 1
    },
    {
        "id": 2,
        "product_name": "Hyundai Centro",
        "is_active": 0
    },
]

fake_resp_aliased = [
    {
        "id": 1,
        "pn": "Hyundai Verna",
        "ia": 1
    },
    {
        "id": 2,
        "pn": "Hyundai Centro",
        "ia": 0
    }
]

fake_resp_aliased_size_1 = [
    {
        "id": 1,
        "pn": "Hyundai Verna",
        "ia": 1
    },
]
fake_db_query1 = "select * from fake_db"

fake_db_response = {
    "data": fake_resp_aliased,
    "totalCount": len(fake_db),
    "currentPageSize": 10,
    "currentPageNumber": 0,
    "hasNext": False
}

fake_db_response_page_size_1 = {
    "data": fake_resp_aliased_size_1,
    "totalCount": len(fake_resp_aliased_size_1),
    "currentPageSize": 1,
    "currentPageNumber": 0,
    "hasNext": False
}


class ProductDetail(BaseModel):
    id: int
    product_name: str = Field(alias="pn")
    is_active: bool = Field(alias="ia")

    class Config:
        allow_population_by_field_name = True


class ProductPage(BaseModel):
    data: List[ProductDetail] = []
    currentPageSize: int
    currentPageNumber: int
    hasNext: bool
    totalCount: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Product(Base):
    __tablename__ = 'fake_product'
    id = Column(Integer, primary_key=True)
    product_name = Column(String(500, 'utf8mb4_unicode_520_ci'), index=True)
    is_active = Column(BIT(1), nullable=False, index=True)


class FakeProductDao(GenericDao):  # noqa
    model = Product


class FakeQueryStrategyV1(NaiveQueryStrategy):

    def get_query(self, *, request=None, dao=None,
                  extra_context: dict = None):
        assert extra_context.get("field_list") == list(ProductDetail.__fields__.keys())
        assert extra_context.get("custom_fields") == False
        assert dao.model == Product
        assert isinstance(dao, FakeProductDao) == True
        return fake_db_query1


class FakeSortingStrategy(SortingOrderStrategy):

    def sort(self, *, query=None, value: Dict[str, str] = None,
             extra_context: dict = None):
        assert value["type"] in ["asc", "dsc"]
        assert query == fake_db_query1
        return query


class FakePaginationStrategyV1(NaivePaginationStrategy):

    def paginate(self, query, request, extra_context: dict):
        pagination_params = utils.jsonify_query_params(request.query_params.get("pagination"))
        assert pagination_params == self.default_pagination_params
        assert query == fake_db_query1
        return {
            "data": fake_db,
            "totalCount": len(fake_db),
            "currentPageSize": pagination_params.get("pageSize"),
            "currentPageNumber": pagination_params.get("page"),
            "hasNext": False
        }


strategy_factory.register_strategy("fake_query_strategy", FakeQueryStrategyV1)
strategy_factory.register_strategy("fake_sorting_strategy", FakeSortingStrategy)
strategy_factory.register_strategy("fake_paginator_strategy", FakePaginationStrategyV1)


class TestListingServiceDefaultFlow(ListingService):
    DEFAULT_SRT_ON = "id"
    dao_kls = FakeProductDao
    QUERY_STRATEGY = "fake_query_strategy"
    SORTING_STRATEGY = "fake_sorting_strategy"
    PAGINATE_STRATEGY = "fake_paginator_strategy"

    def get_listing(self):
        return FastapiListing(self.request, self.dao, ProductDetail).get_response(self.MetaInfo(self))


class FakePaginationStrategyV2(NaivePaginationStrategy):

    def paginate(self, query, request, extra_context: dict):
        pagination_params = utils.jsonify_query_params(request.query_params.get("pagination"))
        assert pagination_params == {"pageSize": 1, "page": 0}
        assert query == fake_db_query1
        return {
            "data": fake_db[:1],
            "totalCount": len(fake_db[:1]),
            "currentPageSize": pagination_params.get("pageSize"),
            "currentPageNumber": pagination_params.get("page"),
            "hasNext": False
        }


strategy_factory.register_strategy("fake_paginator_strategy_v2", FakePaginationStrategyV2)


class TestListinghServiceVariablePageFlow(ListingService):
    DEFAULT_SRT_ON = "id"
    dao_kls = FakeProductDao
    QUERY_STRATEGY = "fake_query_strategy"
    SORTING_STRATEGY = "fake_sorting_strategy"
    PAGINATE_STRATEGY = "fake_paginator_strategy_v2"

    def get_listing(self):
        return FastapiListing(self.request, self.dao, ProductDetail).get_response(self.MetaInfo(self))


class FakeSortingStrategyV2(SortingOrderStrategy):

    def sort(self, *, query=None, value: Dict[str, str] = None,
             extra_context: dict = None):
        assert value["type"] in ["asc", "dsc"], "invalid sorting style!"
        assert query == fake_db_query1

        return query


strategy_factory.register_strategy("fake_sorting_strategy_v2", FakeSortingStrategyV2)


class TestListingServiceSortFlow(ListingService):
    DEFAULT_SRT_ON = "id"
    dao_kls = FakeProductDao
    QUERY_STRATEGY = "fake_query_strategy"
    SORTING_STRATEGY = "fake_sorting_strategy_v2"
    PAGINATE_STRATEGY = "fake_paginator_strategy_v2"

    sort_mapper = {
        "id": "Product.product_id"
    }

    def get_listing(self):
        return FastapiListing(self.request, self.dao, ProductDetail).get_response(self.MetaInfo(self))


def spawn_valueerror_for_strategy_registry(strategy1, strategy2):
    strategy_factory.register_strategy(strategy1, FakePaginationStrategyV2)
    strategy_factory.register_strategy(strategy2, FakePaginationStrategyV2)


def spawn_valueerror_for_filter_factory(field1, field2):
    filter_factory.register_filter(field1, generic_filters.EqualityFilter)
    filter_factory.register_filter(field2, generic_filters.InEqualityFilter)


def invalid_type_factory_keys(factory, key):
    if factory == "filter":
        filter_factory.register_filter(key, generic_filters.EqualityFilter)
    elif factory == "strategy":
        strategy_factory.register_strategy(key, FakePaginationStrategyV2)
    else:
        raise ValueError("Invalid factory selection!")

