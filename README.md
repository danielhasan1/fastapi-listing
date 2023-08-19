# fastapi-listing

Advanced items listing library that gives you freedom to design complex listing APIs that can be read by human.

[![.github/workflows/deploy.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml)
[![.github/workflows/tests.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml) ![PyPI - Programming Language](https://img.shields.io/pypi/pyversions/fastapi-listing.svg?color=%2334D058)
[![codecov](https://codecov.io/gh/danielhasan1/fastapi-listing/branch/dev/graph/badge.svg?token=U29ZRNAH8I)](https://codecov.io/gh/danielhasan1/fastapi-listing)

➡️ Craft powerful Listing APIs designed to serve websites akin to Stack Overflow:

![](https://drive.google.com/uc?export=view&id=1sCkzxi7OirmtA9gGM0LlK9dryI1dlU4U)


## Usage
Its really easy to get started. You can create your very first listing API in 3 steps:

1️⃣ Configure `fastapi-listing` for db `session`:
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
app.add_middleware(DaoSessionBinderMiddleware, master=get_db)
# using master slave architecture?
app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)

# close all sessions implicitly using fastapi-listing in safe mode
app.add_middleware(DaoSessionBinderMiddleware, master=get_db, session_close_implicit=True)
```
2️⃣ How a typical data listing API would look like using `fastapi-listing`:
```python
from fastapi_listing import ListingService, FastapiListing
from fastapi_listing import loader
from app.dao import EmployeeDao # More information is available in docs


@loader.register()
class EmployeeListingService(ListingService):

    default_srt_on = "Employee.emp_no" # configure default field to use for sorting data set.
    default_dao = EmployeeDao # data access object class
    default_page_size = 2 # default page size. accepts dynamic vals from client

    def get_listing(self):
        fields_to_read = ["emp_no", "birth_date", "first_name",
                          "last_name", "gender", "hire_date"] # optional
        resp = FastapiListing(self.request, self.dao, fields_to_fetch=fields_to_read
                              ).get_response(self.MetaInfo(self))
        # don't wanna enter fields manually? using pydantic serializer?
        resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListingDetails
                              ).get_response(self.MetaInfo(self))
        return resp
```

3️⃣ Just call `EmployeeListingService(request).get_listing()` from FastAPI routers:

```python
from fastapi import APIRouter
from fastapi_listing.paginator import ListingPage # Automatic Listing api doc Generation. You can use it as adapter to change meta info in page layout.

from app.service import EmployeeListingService

router = APIRouter(prefix="/emps")

@router.get('/', response_model=ListingPage[EmployeeListingDetail])
def get_emps(request: Request):
    return EmployeeListingService(request).get_listing()
```
Voila 🎉 your very first listing response. (that's even extensible user can manipulate default page structure.)
![](https://drive.google.com/uc?export=view&id=1amgrAdGP7WvXfiNlCYJZPC9fz4_1CidE)


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

* Query
* Filter
* Sorter
* Paginator

You can check out customisation section in docs after going through basics and tutorials.

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

<img src="https://drive.google.com/uc?export=view&id=1C2ZHltxpdyq4YmBsnbOu4HF9JGt6uMfQ" width="600" height="600"/>

# Documentation
View full documentation at: https://fastapi-listing.readthedocs.io ███▓▓░️░️░35%️░️░️░️



# Feedback, Questions?

Any form of feedback and questions are welcome! Please create an issue  💭
[here](https://github.com/danielhasan1/fastapi-listing/issues/new).
