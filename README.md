# fastapi-listing

An Advanced Data Listing Library for fastapi

[![.github/workflows/deploy.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dw/fastapi-listing)[![.github/workflows/tests.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml)

The FastAPI Listing Library is a Python library for building fast, flexible, and customizable listing views in FastAPI web applications. It allows you to easily define listing views for your data models and customize the behavior of those views with minimal code.
## Features

 - Easy-to-use API for listing and formatting data
 - Customizable behavior with minimal code
 - Customizable formatting options, including sorting and filtering
 - Built-in support for pagination, sorting and filtering
 - Built-in support for SQLAlchemy
 - Well defined interface for filter, sorter, paginator
 - The most decoupled API
 - A built-in **semantic** for getting **filters/sorting parameters from clients**
 - Extend anything, swap modules on the fly write n number of versions/strategies
 - The most dry approach you will ever see and create

## Key Components that make a listing
 
 - Data Gateway/Data access object (Dao)
 - Filter applier (Filter application mechanics in case of multiple filterable items)
 - Sorter applier (Sorting application mechanics in case of multiple sorting items)
 - N number of filters
 - Sorter
 - Paginator
 - An orchestrator who orchestrate the above-mentioned phenomenon

Each and every component is provided as module that can be overwritten or extend or 
create a new version with the help of given abstract base classes.

I think all other components are self-explanatory but still I would like to add a little about dao

The idea of a DAO is to keep the code of your application that does the business logic separate from the code that handles how you get and store the data.

Dao is basically a layer that you call to do a thing(create a beautiful query and execute it on demand could be one of this thing) 

Better shown than explain.

# Getting Started
As fastapi is a microframework it allows users to have their own way of defining directory structures unlike django which has a predefined structure
that users follow. I might be using a different directory structure but everything comes down
to the fundamental level of request response lifecycle.

```bash
# what my directory structure looks like.
|-app
   |---dao
   |-----generics
   |-----model
   |---router
   |---schema
   |-----request
   |-----response
   |---service
   |-----strategies
```

To get started using the Fastapi Listing Library, simply install it using pip package manager.

```shell
pip install fastapi-listing
```

Default components are provided out of the box, but they are a bit _naive_ 

Use them where complexities are low and logics are straightforward.

orm of choice is sqlalchemy. Other orms supports will be coming soon.

## Creating your first listing with fastapi-listing

```python
# model file
class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(500, 'utf8mb4_unicode_520_ci'), index=True)
    is_active = Column(BIT(1), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=timezone.istnow())
    created_by = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=timezone.istnow(), onupdate=timezone.istnow())
    updated_by = Column(Integer)
```
```python
#dao file

from fastapi_listing.dao import GenericDao
"""
ClassicDaoFeatures is a baseclass containing generic helper methods
ClassicDaoFeatures inherits from GenericDao which comes with fastapi_listing
Check out GenericDao to see how it looks and how you can leverage it
You can check out this gist https://gist.github.com/danielhasan1/39ed1c8c3f253231b9c57c401db09041
for classicDaoFeatures definition
"""
class ProductDao(ClassicDaoFeatures):
    model = Product # required property, linking our model.
```
```python
# pydantic file
from pydantic import BaseModel, Field
from datetime import datetime


class ProductDetails(BaseModel):
    product_id: int = Field(alias="id")
    product_name: str = Field(alias="pn")
    is_active: bool = Field(alias="ia")
    created_at: datetime = Field(alias="crat")
    created_by: str = Field(alias="crby")
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        

class ProductListingPageResp(BaseModel):
    data: list[ProductDetails]
    hasNext: bool
    currentPageNumber: int
    currentPageSize: int
    totalCount: int
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
```

```python
# listing service file

# base class to be used for every new listing class
from fastapi_listing import ListingService
# orchestrator class inheriting is forbidden
from fastapi_listing import FastapiListing
# a module of generic_filters you can look for how they are implemented and how you can create 
# your custom filters
from fastapi_listing.filters import generic_filters
# a factory containing all registered filters with unique keys
from fastapi_listing.factory import filter_factory
# pydantic schema will be used by listing to only load required fields from table 
from app.schema.response import ProductDetails


# registering filter definitions with key followed by its definition
# as multiple tables can have same name and filter_factory expects a unique registeration key
# model.column is used as key for the definition
filter_factory.register_filter("Product.product_name", generic_filters.StringContainsFilter)
filter_factory.register_filter("Product.is_active", generic_filters.EqualityFilter)


# create a listing class inheriting base ListingService
class ProductListingService(ListingService):
    # filter mapper format
    # here you tell which filter you wanna use 
    # on this listing service
    # I'm using pydantic aliases as key and modelname.column as value
    # these aliases will get exposed to client and not our actual field names
    # to keep them hidden
    
    # allowed filters that listing is aware of
    filter_mapper = {
        "pn": "Product.product_name",
        "ia": "Product.is_active",
    }
    
    # default sorting column to use when api is called raw
    DEFAULT_SRT_ON = ProductDao.model.created_at.name #required
    dao_kls = ProductDao # required

    def get_listing(self):
        # injecting pydantic shcema to load only shcema related fields
        # note to make : pydantic model should only contain model related column
        # to dynamically load them any unidentified column name that doesnt exists will result in an error
        # still if you are generating some fields at runtime
        # and still wanting to load field from pydantic model then pass
        # custom_fields flag as well. this will suppress unidentified fields error
        resp = FastapiListing(self.request, self.dao, ProductDetails).get_response(self.MetaInfo(self))
        return resp
```

```python
# router file

from fastapi import APIRouter, Request
# imported listing service
from app.service import ProductListingService
from app.schema.response import ProductListingPageResp
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session


prod_v1 = APIRouter(
    prefix="/v1/products", tags=["product"]
)

def get_db():
    """
    Get SQLAlchemy database session
    
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
        
def get_read_db():
    """
    Get SQLAlchemy read database session
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
        
# added support for read_db, write_db separately. I understand many users migh be using single db for
# everything and they still could refere same session on read_db, write_db.
# I would suggest using both as it will allow us to lay out future ground work for when we decide
# to separate our db operation on basis of type. so once we decide to go with it it will only allow
# us to easily implement things with minimal changes at the gateway i.e., router where we create db sessions.
# rest of our code will look exactly same.

@prod_v1.get("", response_model=ProductListingPageResp)
def get_prod_mapping_listing(request: Request, read_db: Session = Depends(get_db),
                             write_db: Session = Depends(get_read_db)):
    service_obj = ProductListingService(request, read_db=read_db)
    return service_obj.get_listing()

```
## if everything goes right above snippet should produce something like this
```json

    {
    "data": [
        {
            "id": 51100313,
            "pn": "OnePlus 3T",
            "ia": false,
            "crat": "05/05/2023, 23:47:02",
            "crby": "John",
        },
        {
            "pid": 11123121,
            "pnm": "Samsung Galaxy M32 5G",
            "ia": true,
            "crat": "05/05/2023, 23:47:02",
            "crby": "Mark",

        },
        {
            "pid": 12121,
            "pnm": "Asus VivoBook S14 S433EA-AM502TS",
            "ia": true,
            "crat": "05/05/2023, 23:47:02",
            "crby": "Lia",

        },
        {
            "pid": 9111894,
            "pnm": "tests",
            "ia": true,
            "crat": "05/05/2023, 23:47:02",
            "crby": "Hugh",
        }
    ],
    "hasNext": false,
    "currentPageNumber": 0,
    "currentPageSize": 10,
    "totalCount": 4
}
```
## Client Site Filter Semantic

fastapi-listing support has built-in filter semantics rule
with this it can distinguish whether to apply listing filter or not. 

Rreserved `filter` keyword in uri, it highlights that client want to send everything that is coupled with this keyword
will be traversed by fastapi-listing library.

example - 
if your api call is `/v1/products` and if you want to apply a name filter
then client side should send a query param with reserved key like
`?filter=[{"field":"pn","value":{"search":"Some name"}]`

just like this other filters should append inside the list as well.
`?filter=[{"field":"pn","value":{"search":"Some name"}, {"field":"ia","value":{"search":true}]`
 
similarly for sorter
`?sort=[{"field":"crat" "type":asc}]` and `?pagination={"pageSize": 10, "page": 0}`
fastapi-listing will extract all three keys value and use them to process listing data.

**note** here we are using aliases and not the actual field names to avoid exposing
our fields or table information to avoid any possible injection attacks.
mappers are provided to our listing services to deduce actual fields at runtime.


# Customization
## Adding our extendable query strategy which we can extend infinitely
We also need to show updated by field in the listing 
created_by and updated by could contain different user ids, so we need to handle 
this by writing our own custom query lets see how we can implement this,
now we will be extending our existing code

```python
# in our pydantic file we will add a new version of our response

class ProductDetailsV2(ProductDetails):
    updated_at: datetime = Field(alias="upat")
    updated_by: str = Field(alias="upby")
```
```python

# in dao file we will be adding a new method
# segregating the query call we could also name the query as abc_query_v1 to add named versions
# so if we are changing our query we won't change the original one but add a new version.

from fastapi_listing.typing import SqlAlchemyQuery
from sqlalchemy.orm import aliased
from sqlalchemy.sql import functions
from app.dao.model import Product, User

class ProductDao(ClassicDaoFeatures): # ClassicDaoFeatures is a baseclass containing generic helper methods
    model = Product # required property, linking our model.

    def get_base_query(self) -> SqlAlchemyQuery:
        # Our custom query
        UserA = aliased(User)
        UserB = aliased(User)
        # we need to join with user table twice to get 
        # created by and updated names at the same time
        # not a query that you may want to use in production
        # but still separating queries in dao will be a bliss in future
        # when you will have lots of queries
        # specially cases when you are working on large pages like dashboards
        # where you are loading tons of listing data
        # you can easily write a version2..version n query
        # and use it in your query strategy
        # implementing extension or changes to places that needs changes
        # and won't be touching places that doesn't need changes.
        query = self._read_db.query(self.model.product_id, self.model.product_name,
                                    self.model.created_at, self.model.updated_at,
                                    self.model.is_active, UserA.firstName.label("created_by"),
                                    UserB.firstName.label("updated_by")
                                    ).join(UserA,
                                           self.model.created_by == UserA.id
                                           ).join(UserB,
                                                  self.model.updated_by == UserB.id)
        return query
```
now we will create a new file in our strategy folder

```python
# product query strategy file - a handler to call required query from dao laye, this interface decides
# what you want to access and how you want to access it
from fastapi_listing.strategies import NaiveQueryStrategy
from fastapi_listing.typing import FastapiRequest, SqlAlchemyQuery
from fastapi_listing.factory import strategy_factory
from app.dao import ProductDao

NAME = "prod_query" # module name intentionally declaring a constant


class ProductQueryStrategy(NaiveQueryStrategy):

    def get_query(self, *, request: FastapiRequest = None, dao: ProductDao = None,
                  extra_context: dict = None) -> SqlAlchemyQuery:
        query = dao.get_base_query()
        return query



strategy_factory.register_strategy(NAME, ProductDao) # registering our strategy with unique name

```


```python
# rest of the imports as initial
# importing our created strategy 
from app.service.strategies import prod_query_strtg


class ProductListingService(ListingService):
    filter_mapper = {
        "pnm": "Product.product_name",
        "ia": "Product.is_active",
    }
    DEFAULT_SRT_ON = LgxAsmtProdMapDao.model.created_at.name
    dao_kls = LgxAsmtProdMapDao
    QUERY_STRATEGY = prod_query_strtg.NAME # linking our query strategy

    def get_listing(self):
        # note here we have removed pydantic class to load fields 
        # as in our custom query we are loading it manually 
        # when we are writing our query we are in full control of what
        # we are trying to look for, and how we wanna look at it/ load it
        resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
        return resp
```


## This will return something like this

```json
{
    "data": [
        {
            "id": 1500121313,
            "pnm": "OnePlus 3T",
            "ia": false,
            "crat": "05/05/2023, 23:47:02",
            "crby": "John",
            "upat": "05/05/2023, 23:47:02",
            "upby": "Hugh"
        },
        {
            "pid": 12112341,
            "pnm": "Samsung Galaxy M32 5G",
            "ia": true,
            "crat": "05/05/2023, 23:47:02",
            "crby": "Will",
            "upat": "05/05/2023, 23:47:02",
            "upby": "Shawn"
        },
        {
            "pid": 121123422,
            "pnm": "Asus VivoBook S14 S433EA-AM502TS",
            "ia": true,
            "crat": "05/05/2023, 23:47:02",
            "crby": "Hugh",
            "upat": "05/05/2023, 23:47:02",
            "upby": "Jack"
        },
        {
            "pid": 1112112,
            "pnm": "tests",
            "ia": true,
            "crat": "05/05/2023, 23:47:02",
            "crby": "Navdeep",
            "upat": "05/05/2023, 23:47:02",
            "upby": "Jonas"
        }
    ],
    "hasNext": false,
    "currentPageNumber": 0,
    "currentPageSize": 10,
    "totalCount": 4
}
```

We can even customise the default page template
key val binding like 
data, hasNext etc
We can write our own custom paginator or extend the existing one
to support our existing client side page rendering logic.

```python
# Default pagination strategy
# want to change it import it 
# this is where you prepare your page. you can write n number of versions
# and still manage your code beautifully


# from  fastapi_listing.strategies import NaivePaginationStrategy



class NaivePaginationStrategy(TableDataPaginatingStrategy):
    """
    Loosely coupled paginator module.
    design your own paginator as you want.
    you can even decide which request param you want to use as paginator identifier
    by default we take it as ?pagination={"pageSize": 10, "page": 0}
    Inherit from this class change pagination as you may like,
    plug this pagination to your listing service
    register this strategy with factory and voila
    you can see your page rendering just like you defined
    """

    default_pagination_params = {"pageSize": 10, "page": 0} # orchestrator will read these
    
    PAGE_TEMPLATE = {"data": None, "hasNext": None, "totalCount": None,
                     "currentPageSize": None, "currentPageNumber": None}

    def paginate(self, query: SqlAlchemyQuery, request: FastapiRequest, extra_context: dict):
        pagination_params = self.default_pagination_params
        try:
            # extracting pagination queryparam given by client request
            # if not given then will be using default_pagination_params
            pagination_params = utils.jsonify_query_params(request.query_params.get('pagination')) \
                if request.query_params.get('pagination') else pagination_params
        except JSONDecodeError:
            raise ListingPaginatorError("pagination params are not valid json!")
        count = query.count()
        # mysql limit offset logic to paginate table data.
        # not recommended for large tables 
        # implement your own pagination class or extend this as much as you like
        # for as many listing as you like with clean/clear/dry/decoupled codeflow.
        has_next = True if count - ((pagination_params.get('page')) * pagination_params.get('pageSize')) > \
                           pagination_params.get('pageSize') else False
        current_page_size = pagination_params.get("pageSize")
        current_page_number = pagination_params.get("page")
        query = query.limit(
            pagination_params.get('pageSize')
        ).offset(
            (pagination_params.get('page')) * pagination_params.get('pageSize')
        )
        # page response which will finally be delivered back to client site for rendering or processing
        page = dict(data=query.all(), hasNext=has_next, totalCount=count, currentPageSize=current_page_size,
                    currentPageNumber=current_page_number)
        return page
```

```python

"""
Many filters are provided built in to ease your life, still you can create your own filters
on the fly, inherit existing filters or write your custom ones it easier than ever.

filter definition is in 
from fastapi_listing.filters import generic_filters 
"""
# filter definition
# you can take inspiration of how you may wanna create your own custom filter
# check out CommonFilterImpl to see provided class attribute 
class EqualityFilter(CommonFilterImpl):
    
    # method which will filter the query
    def filter(self, *, field=None, value=None, query=None) -> SqlAlchemyQuery:
        # not following the standard way of adding fields, pass your own hook
        # to extract fields as you like
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field == value.get("search"))
        # filtered query will be return to iterative filter mechanics
        # if you have multiple filters then all filters will get applied lazily
        # in iterative manner
        return query
```



More info will be coming soon in docs.

# Feedback, Questions?

Any form of feedback and questions are welcome! Please create an issue
[here](https://github.com/danielhasan1/fastapi-listing/issues/new).