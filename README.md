# fastapi-listing

Advanced items listing library that gives you freedom to design complex listing APIs that can be read by human.

[![.github/workflows/deploy.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml)
[![.github/workflows/tests.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml) ![PyPI - Programming Language](https://img.shields.io/pypi/pyversions/fastapi-listing.svg?color=%2334D058)
[![codecov](https://codecov.io/gh/danielhasan1/fastapi-listing/branch/dev/graph/badge.svg?token=U29ZRNAH8I)](https://codecov.io/gh/danielhasan1/fastapi-listing) [![Downloads](https://static.pepy.tech/badge/fastapi-listing)](https://pepy.tech/project/fastapi-listing)

➡️ Craft powerful Listing REST APIs designed to serve websites akin to Stack Overflow:

![](https://drive.google.com/uc?export=view&id=1sCkzxi7OirmtA9gGM0LlK9dryI1dlU4U)

Comes with:
- pre defined filters
- pre defined paginator
- pre defined sorter

## Advantage
- simplify the intricate process of designing and developing complex listing APIs
- Design components(USP) and plug them from anywhere
- Components can be **reusable**
- Best for fast changing needs

## Usage

➡️ With the New Compact Version(Older version was provided with a guide style which is supported by this version as well)
create your listing API in 2 easy steps 🥳

1️⃣ Create a Dao (Data Access Object) layer (a simple class)

```python
from fastapi_listing.dao import GenericDao
from app.model import Employee


# your dao (data access object) placed here for the sake of example
class EmployeeDao(GenericDao):
    """write your data layer access logic here. keep it raw!"""
    name = "employee"
    model = Employee # your sqlalchemy model, support for more orm is coming soon
```
2️⃣ Just call `FastapiListing`

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# import fastapi-listing dependencies
from fastapi_listing.paginator import ListingPage # default pydantic page model, you can create/extend your own
from fastapi_listing import FastapiListing, MetaInfo

app = FastAPI()  # create FastAPI app

def get_db() -> Session:
    """
    replicating sessionmaker for any fastapi app.
    anyone could be using a different way or opensource packages to produce sessions.
    it all comes down to a single result that is yielding a session.
    for the sake of simplicity and testing purpose I'm replicating this behaviour in this way.
    :return: Session
    """



# your pydantic response class if you are using one
# Supports pydantic v2
class EmployeeListDetails(BaseModel):
    emp_no: int = Field(alias="empid", title="Employee ID")
    birth_date: date = Field(alias="bdt", title="Birth Date")
    first_name: str = Field(alias="fnm", title="First Name")
    last_name: str = Field(alias="lnm", title="Last Name")
    gender: str = Field(alias="gdr", title="Gender")
    hire_date: date = Field(alias="hdt", title="Hiring Date")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
    
@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(db=Depends(get_db)):
    dao = EmployeeDao(read_db=db)
    # passing pydantic serializer is optional, automatically generates a
    # select query based on pydantic class fields for easy cases like columns of same table
    return FastapiListing(dao=dao, pydantic_serializer=EmployeeListDetails
                          ).get_response(MetaInfo(default_srt_on="emp_no"))    
```

Voila 🎉 your very first listing response(that's even extensible user can manipulate default page structure)

![](https://drive.google.com/uc?export=view&id=1amgrAdGP7WvXfiNlCYJZPC9fz4_1CidE)


Your pydantic class contains some dynamic fields that you populate at runtime❓️

```python
@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(db=Depends(get_db)):
    dao = EmployeeDao(read_db=db)
    return FastapiListing(dao=dao,
                          pydantic_serializer=EmployeeListDetails, # optional
                          custom_fields=True # just tell fastapi-listing that your model contains custom_fields
                          ).get_response(MetaInfo(default_srt_on="emp_no"))
```

Auto generated query  doesn't fulfil your use case❓️

```python
class EmployeeDao(GenericDao):
    """write your data layer access logic here. keep it raw!"""
    name = "employee"
    model = Employee
    
    def get_default_read(self, fields_to_read: Optional[list]):
        """
        Extend and return your query from here.
        Use it when use cases are comparatively easier than complex.
        Alternatively fastapi-listing provides a robust way to write performance packed queries 
        for complex APIs which we will look at later.
        """
        query = self._read_db.query(Employee)
        return query
```

```python
@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(db=Depends(get_db)):
    dao = EmployeeDao(read_db=db)
    return FastapiListing(dao=dao).get_response(MetaInfo(default_srt_on="emp_no"))
```


## Thinking about adding filters???
Don't worry I've got you covered😎

➡️ Say you want to add filter on Employee for:
1.  gender - return only **Employees** belonging to 'X' gender where X could be anything.
2.  DOB - return **Employees** belonging to a specific range of DOB.
3.  First Name - return **Employees** only starting with specific first names.
```python
from fastapi_listing.filters import generic_filters # collection of inbuilt filters
from fastapi_listing.factory import filter_factory # import filter_factory to register filter against a listing

# {"alias": ("<model.field>", "<filter_definition>")}
emp_filter_mapper = {
    "gdr": ("Employee.gender", generic_filters.EqualityFilter),
    "bdt": ("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter),
    "fnm": ("Employee.first_name", generic_filters.StringStartsWithFilter),
}
filter_factory.register_filter_mapper(emp_filter_mapper) # You just registered the number of filters allowed to client on this listing


@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(request: Request, db=Depends(get_db)):
    """
    request is optional to pass.
    you can pass filter query_param or use request object.
    make fastapi-listing adapt to your client existing query_param format
    """
    dao = EmployeeDao(read_db=db)
    return FastapiListing(request=request, dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no", filter_mapper=emp_filter_mapper))
    
```

Thinking about how fastapi-listing reads filter/sorter/paginator params❓️

```python
# Extend adapter to make fastapi-listing adapt your existing clients

# default implementation

from fastapi_listing.service.adapters import CoreListingParamsAdapter

class YourAdapterClass(CoreListingParamsAdapter): # Extend to add your behaviour
    """Utilise this adapter class to make your remote client site:
    - filter,
    - sorter,
    - paginator.
    query params adapt to fastapi listing library.
    With this you can utilise same listing api to multiple remote client
    even if it's a front end server or other backend server.

    core service is always going to request one of the following fundamental key
    - sort
    - filter
    - pagination
    depending upon this return the appropriate transformed client param back to fastapi listing
    supported formats for
    filter:
    simple filter - [{"field":"<key used in filter mapper>", "value":{"search":"<client param>"}}, ...]
    if you are using a range filter -
    [{"field":"<key used in filter mapper>", "value":{"start":"<start range>", "end": "<end range>"}}, ...]
    if you are using a list filter i.e. search on given items
    [{"field":"<key used in filter mapper>", "value":{"list":["<client params>"]}}, ...]

    sort:
    [{"field":<"key used in sort mapper>", "type":"asc or "dsc"}, ...]
    by default single sort allowed you can change it by extending sort interceptor

    pagination:
    {"pageSize": <integer page size>, "page": <integer page number 1 based>}
    """
    
    def get(self, key: Literal["sort", "filter", "pagination"]):
        """
        @param key: Literal["sort", "filter", "pagination"]
        @return: List[Optional[dict]] for filter/sort and dict for paginator
        """
        return utils.dictify_query_params(self.dependency.get(key))

```
Pass request or extract feature(filter/sorter/paginator) params at router and pass them as kwargs

```python

@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(request: Request, db=Depends(get_db)):
    params = request.query_params
    # filter, sort. pagination = params.get("filter"), params.get("sort"), params.get("paginator")
    # you can pass above args as kwargs in MetaInfo
    dao = EmployeeDao(read_db=db)
    return FastapiListing(request=request, dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no", filter_mapper=emp_filter_mapper, feature_params_adapter=YourAdapterClass))
    
```

Check out [docs](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#adding-filters-to-your-listing-api) for supported list of filters.
Additionally, you can create **custom filters** as well.

## Thinking about adding Sorting???
I won't leave you hanging there as well😎
```python
@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(request: Request, db=Depends(get_db)):
    # define it here or anywhere
    emp_sort_mapper = {
        "cd": "Employee.emp_no",
        "bdt": "Employee.birth_date"
    }
    dao = EmployeeDao(read_db=db)
    return FastapiListing(request=request, dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no", filter_mapper=emp_filter_mapper, feature_params_adapter=YourAdapterClass,
                 sort_mapper=emp_sort_mapper))
```

## Provided features are not meeting your requirements???

It is customizable.😎

➡️ You can write custom:

* Query
* Filter
* Sorter
* Paginator

You can check out customisation section in docs after going through basics and tutorials.

Check out my other [repo](https://github.com/danielhasan1/test-fastapi-listing/blob/master/app/router/router.py) to see some examples

## Features and Readability hand in hand 🤝

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
