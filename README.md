# fastapi-listing

An Advanced Data Listing Library for fastapi

[![.github/workflows/deploy.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml)
[![.github/workflows/tests.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml) ![PyPI - Programming Language](https://img.shields.io/pypi/pyversions/fastapi-listing.svg?color=%2334D058)
[![codecov](https://codecov.io/gh/danielhasan1/fastapi-listing/branch/dev/graph/badge.svg?token=U29ZRNAH8I)](https://codecov.io/gh/danielhasan1/fastapi-listing)


A Python library for building fast, extensible, and customizable data listing APIs.

![](/imgs/simple_response.png)

## Usage
➡️ Configure `fastapi-listing` for db `session`:
```python
from fastapi import FastAPI
from sqlalchemy.orm import Session

from fastapi_listing.middlewares import DaoSessionBinderMiddleware

def get_db() -> Session:
    """
    replicating sessionmaker for any fastapi app.
    anyone could be using a different way or opensource packages to produce sessions.
    it all comes down to a single result that is yielding a session.
    for the sake of simplicity and testing purpose I'm replicating this behaviour in this way.
    :return: Session
    """

    
app = FastAPI()

# with this - use dao classes powered by sqlalchemy sessions anywhere in your project. no more passing sessions as args 
# here and there.
app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)
```
➡️ How a typical data listing API would look like using `fastapi-listing`:
```python
from fastapi_listing import ListingService, FastapiListing
from fastapi_listing import loader
from app.dao import EmployeeDao # More information is available in docs


@loader.register()
class EmployeeListingService(ListingService):

    default_srt_on = "Employee.emp_no" # configure default field to use for sorting data set.
    default_dao = EmployeeDao
    default_page_size = 2 # default page size. accepts dynamic vals from client

    def get_listing(self):
        fields_to_read = ["emp_no", "birth_date", "first_name",
                          "last_name", "gender", "hire_date", "image"]
        resp = FastapiListing(self.request, self.dao, fields_to_fetch=fields_to_read
                              ).get_response(self.MetaInfo(self))
        return resp
```

➡️ Just call `EmployeeListingService(request).get_listing()` from FastAPI routers:

```python
from fastapi import APIRouter
from fastapi_listing.paginator import ListingPage # Automatic Listing api doc Generation. You can use it as adapter to change meta info in page layout.

from app.service import EmployeeListingService

router = APIRouter(prefix="/emps")

@router.get('/', response_model=ListingPage[EmployeeListingDetail])
def get_emps(request: Request):
    return EmployeeListingService(request).get_listing()
```

![](/imgs/simple_response2.png)

➡️ Use pydantic to avoid re-writing field_to_fetch:
```python
@loader.register()
class EmployeeListingService(ListingService):

    default_srt_on = "Employee.emp_no"
    default_dao = EmployeeDao
    default_page_size = 2

    def get_listing(self):
        # your pydantic model contains custom non sqlalchemy model fields? pass custom_fields=True
        resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListingDetail
                              ).get_response(self.MetaInfo(self))
        return resp
        
```

## Thinking about adding filters???
Don't worry I've got you covered😎

➡️ Say you want to add filter on Employee for:
1.  gender - return only **Employees** belonging to 'X' gender where X could be anything.
2.  DOB - return **Employees** belonging to a specific range of DOB.
3.  First Name - return **Employees** only starting with specific first names.
```python
from fastapi_listing.filters import generic_filters # collection of inbuilt filters


@loader.register()
class EmployeeListingService(ListingService):

    filter_mapper = {
        "gdr": ("Employee.gender", generic_filters.EqualityFilter),
        "bdt": ("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter),
        "fnm": ("Employee.first_name", generic_filters.StringStartsWithFilter),
    }
    
```
Check out [docs](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#adding-filters-to-your-listing-api) for supported list of filters.
Additionally, you can create **custom filters** as well. Check reference below 📝.
## Thinking about adding Sorting???
I won't leave you hanging there as well😎
```python
@loader.register()
class EmployeeListingService(ListingService):
    sort_mapper = {
        "cd": "Employee.emp_no",
        "bdt": "Employee.birth_date"
    }

```
## Provided features are not meeting your requirements???
It is customizable.😎

➡️ You can write custom:

[Query](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#customising-your-listing-query)

[Filters](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#customising-your-filters)

[Sorter](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#adding-sorters-to-your-listing-api)

[Paginator](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#pagination-strategy)

## Features

 - Easy-to-use API for listing and formatting data
 - Built-in support for pagination, sorting and filtering
 - Well defined interface for filter, sorter, paginator
 - Support Dependency Injection for easy testing
 - Room to adapt the existing remote client query param semantics
 - Write standardise listing APIs that will be understood by generations of upcoming developers
 - Write listing features which is easy on human mind to extend or understand
 - Break down the most complex listing data APIs into digestible piece of code 

With FastAPI Listing you won't end up like

![](/imgs/meme_read_somones_code.jpg)

# Documentation
View full documentation at: https://fastapi-listing.readthedocs.io ██▓░️░️░️░️░️░️░️



# Feedback, Questions?

Any form of feedback and questions are welcome! Please create an issue  💭
[here](https://github.com/danielhasan1/fastapi-listing/issues/new).