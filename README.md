# fastapi-listing

A listing API library for FastAPI, built around small, composable components rather than one large
endpoint function.

[![.github/workflows/deploy.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/deploy.yml)
[![.github/workflows/tests.yml](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml/badge.svg)](https://github.com/danielhasan1/fastapi-listing/actions/workflows/tests.yml) ![PyPI - Programming Language](https://img.shields.io/pypi/pyversions/fastapi-listing.svg?color=%2334D058)
[![codecov](https://codecov.io/gh/danielhasan1/fastapi-listing/branch/dev/graph/badge.svg?token=U29ZRNAH8I)](https://codecov.io/gh/danielhasan1/fastapi-listing) [![Downloads](https://static.pepy.tech/badge/fastapi-listing)](https://pepy.tech/project/fastapi-listing)

> **Upgrading to 0.4.0?** It's a breaking change **only** if you wrote a custom `Filter`/`Sorter`/`QueryStrategy`/
> `PaginationStrategy` subclass - the plain `GenericDao` + `generic_filters` + default-strategies flow below is
> unaffected. See [CHANGELOG.md](CHANGELOG.md) for the migration table.

Comes with:
- a predefined set of filters
- a predefined paginator
- a predefined sorter
- SQLAlchemy support out of the box, and a backend-agnostic core so you're not locked into one ORM

## Why

- Simplifies designing and maintaining complex listing APIs
- Components are independent, reusable, and can be swapped in from anywhere
- Well suited to fast-changing requirements
- Not an ORM captive: filters/sorter/paginator are written against a small `QueryContext` contract, not a raw SQLAlchemy `Query` - swap in a different backend without rewriting your filters

## Installing

Using [pip](https://pip.pypa.io/):

```bash
pip install fastapi-listing
```

## Quick example

The example below runs against the [MySQL employee sample DB](https://dev.mysql.com/doc/employee/en/).

There are two ways to implement a listing API with this library: **inline** or **class-based**. Both
need a DAO (data access object) class.

### Inline implementation

```python
# main.py

from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import date

from sqlalchemy import Column, Date, Enum, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

from fastapi_listing.paginator import ListingPage
from fastapi_listing import FastapiListing, MetaInfo
from fastapi_listing.dao import GenericDao


Base = declarative_base()
app = FastAPI()


class Employee(Base):
    __tablename__ = 'employees'

    emp_no = Column(Integer, primary_key=True)
    birth_date = Column(Date, nullable=False)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(Enum('M', 'F'), nullable=False)
    hire_date = Column(Date, nullable=False)

# Dao class
class EmployeeDao(GenericDao):
    """Data access logic lives here - keep it raw."""
    name = "employee"
    model = Employee  # SQLAlchemy model class. Not on SQLAlchemy? See "Backend support" below.


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
def get_employees(db: Session):
    dao = EmployeeDao(read_db=db)
    # passing a pydantic serializer is optional - it generates a select query from the
    # serializer's fields for simple cases (columns all on the same table); otherwise
    # provide the select query yourself in the DAO layer
    return FastapiListing(dao=dao, pydantic_serializer=EmployeeListDetails
                          ).get_response(MetaInfo(default_srt_on="emp_no"))  # sorts descending by default
```

If your Pydantic model has computed fields (fields with no matching column), pass `custom_fields=True` to
avoid an "unknown attribute" error:

```python
@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(db: Session):
    dao = EmployeeDao(read_db=db)
    return FastapiListing(dao=dao,
                          pydantic_serializer=EmployeeListDetails,
                          custom_fields=True
                          ).get_response(MetaInfo(default_srt_on="emp_no"))
```

That's your first listing response.

![](https://drive.google.com/uc?export=view&id=1amgrAdGP7WvXfiNlCYJZPC9fz4_1CidE)

If the auto-generated query doesn't fit your use case, override `get_default_read` in the DAO instead:

```python
# Overwriting default read method in dao class
class EmployeeDao(GenericDao):
    """Data access logic lives here - keep it raw."""
    name = "employee"
    model = Employee

    def get_default_read(self, fields_to_read: Optional[list]):
        """
        Extend and return your query from here.
        Use this when the use case is simpler than a full custom query strategy;
        for more complex cases, see the query-customisation docs.
        """
        query = self._read_db.query(Employee)
        return query


@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(db: Session):
    dao = EmployeeDao(read_db=db)
    # note the optional named params are gone here
    return FastapiListing(dao=dao).get_response(MetaInfo(default_srt_on="emp_no"))
```


## Adding client-site features

Before adding filters, sorters, or pagination, most existing services need one bit of setup: an adapter
that reads your client's actual request-parameter format, unless it already matches FastAPI Listing's
native format exactly.

### Add a custom adapter for reading filter/sorter/paginator parameters

Below is the default implementation - you'll typically extend it with your own parameter format.

```python
from typing import Literal
from fastapi_listing.service.adapters import CoreListingParamsAdapter
from fastapi_listing import utils

class YourAdapterClass(CoreListingParamsAdapter):  # extend to add your own behavior
    """Adapts your client's filter/sorter/paginator query params to what FastAPI
    Listing expects natively. This lets the same listing API serve multiple
    clients - a frontend, another backend service, whatever - each using their
    own parameter format.

    FastAPI Listing looks for up to three keys:
    - sort
    - filter
    - pagination

    Supported formats:

    filter:
      single value  - [{"field": "<key in filter_mapper>", "value": {"search": "<client value>"}}, ...]
      range         - [{"field": "<key in filter_mapper>", "value": {"start": "<start>", "end": "<end>"}}, ...]
      list          - [{"field": "<key in filter_mapper>", "value": {"list": ["<values>"]}}, ...]

    sort:
      [{"field": "<key in sort_mapper>", "type": "asc" | "dsc"}, ...]
      single-field sort by default; extend the sort interceptor for multi-field sort.

    pagination:
      {"pageSize": <int>, "page": <int, 1-based>}
    """

    def get(self, key: Literal["sort", "filter", "pagination"]):
        """
        @param key: Literal["sort", "filter", "pagination"]
        @return: List[Optional[dict]] for filter/sort, dict for pagination
        """
        return utils.dictify_query_params(self.dependency.get(key))

```

### Adding filters

Add filters on `Employee` for:
1. **gender** - only employees matching a given gender
2. **date of birth** - employees within a date range
3. **first name** - employees whose first name starts with a given value

```python
from fastapi import Request
from sqlalchemy.orm import Session

from fastapi_listing.paginator import ListingPage
from fastapi_listing.filters import generic_filters  # collection of inbuilt filters
from fastapi_listing.factory import filter_factory  # register a filter mapper for use
from fastapi_listing import MetaInfo, FastapiListing


emp_filter_mapper = {
    "gdr": ("Employee.gender", generic_filters.EqualityFilter),
    "bdt": ("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter),
    "fnm": ("Employee.first_name", generic_filters.StringStartsWithFilter),
}
filter_factory.register_filter_mapper(emp_filter_mapper)


@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(request: Request, db: Session):
    dao = EmployeeDao(read_db=db)
    return FastapiListing(request=request, dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no",
                 filter_mapper=emp_filter_mapper,
                 feature_params_adapter=YourAdapterClass))
```

If you'd rather not pass the request object through, extract what you need and pass it directly instead:

```python
@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(request: Request, db: Session):
    params = request.query_params
    filter_, sort_, pagination = params.get("filter"), params.get("sort"), params.get("paginator")

    dao = EmployeeDao(read_db=db)
    return FastapiListing(dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no",
                 filter_mapper=emp_filter_mapper,
                 feature_params_adapter=YourAdapterClass,
                 filter=filter_,
                 sort=sort_,
                 paginator=pagination))
```

### Breaking it down

**Filter mapper** - the set of filters allowed on this listing API. A request for anything outside this
mapper is simply not executed, which keeps clients from probing for fields you didn't intend to expose.

`generic_filters` is a collection of inbuilt filters supported by the SQLAlchemy ORM. The mapper's
structure:

`{"alias": tuple("sqlalchemy_model.field", filter_implementation)}`

`alias` - what the client sends, so the real column name never has to be exposed.

`tuple` - the field name and the filter implementation.

```python
from fastapi_listing.filters import generic_filters


emp_filter_mapper = {
    "gdr": ("Employee.gender", generic_filters.EqualityFilter),
    "bdt": ("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter),
    "fnm": ("Employee.first_name", generic_filters.StringStartsWithFilter),
}
```

Register the mapper with the filter factory, at module level:

```python
from fastapi_listing.factory import filter_factory


filter_factory.register_filter_mapper(emp_filter_mapper)
```

A client could then request `v1/employees?filter=[{"gdr":"M"}]`, which your adapter parses into
`[{"field":"gdr", "value":{"search":"M"}}]` - if the adapter is given kwargs directly rather than the
request, access them via `self.extra_context`; if it's given the request, access `self.request`
directly.

That produces a response filtered to rows where `gender` is `M`.

**Sort mapper** - the set of fields allowed for sorting; a request for anything outside this mapper is
not permitted.

Structure: `{"alias": "field"}` - omit the model name when sorting on the primary model's own column, or
qualify it (`{"alias": "sqlalchemy_model.field"}`) for a joined table's column, same as with filters.

```python
listing_sort_mapper = {
        "code": "emp_no"
    }
return FastapiListing(dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no",
                 filter_mapper=emp_filter_mapper,
                 sort_mapper=listing_sort_mapper,
                 feature_params_adapter=YourAdapterClass,
                 filter=filter_,
                 sort=sort_,
                 paginator=pagination))

# or, passing the request object instead
return FastapiListing(request=request, dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no",
                 filter_mapper=emp_filter_mapper,
                 sort_mapper=listing_sort_mapper,
                 feature_params_adapter=YourAdapterClass))
```

A client could then request `v1/employees?sort={"code":<some_code:int>}`, or combine it with a filter -
`v1/employees?filter=[{"gdr":"M"}]&sort={"code":<some_code:int>, "type":"asc"}` - and the response would
be sorted by employee code, ascending.

**Note**: unlike the filter mapper, the sort mapper doesn't need to be registered with a factory.

Pagination works the same way: `v1/employees?pagination={"page":1, "pageSize":10}`, or combined with
filter and sort - `v1/employees?filter=[{"gdr":"M"}]&sort={"code":<some_code:int>, "type":"asc"}&pagination={"page":1, "pageSize":10}`.

That returns a page of 10 items, or however many the client requests via `pageSize`.

By default, FastAPI Listing caps a single request at 50 items to protect the database. Change that (and
the default page size) via `MetaInfo`:

```python
return FastapiListing(request=request, dao=dao).get_response(
        MetaInfo(default_srt_on="emp_no",
                 filter_mapper=emp_filter_mapper,
                 sort_mapper=listing_sort_mapper,
                 max_page_size=25,       # cap on requested page size
                 default_page_size=10,   # page size when the client doesn't specify one
                 feature_params_adapter=YourAdapterClass))
```

### Class-based implementation

The same listing API, structured as a class:

```python
from fastapi import FastAPI

from sqlalchemy import Column, Date, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session, relationship
from fastapi_listing import ListingService, FastapiListing
from fastapi_listing.filters import generic_filters
from fastapi_listing import loader
from fastapi_listing.paginator import ListingPage

Base = declarative_base()
app = FastAPI()

class Title(Base):
    __tablename__ = 'titles'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    title = Column(String(50), primary_key=True, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date)

    employee = relationship('Employee')


class EmployeeDao(GenericDao):
    name = "employee"
    model = Employee

class TitleDao(GenericDao):
    name = "title"
    model = Title

@loader.register()
class EmployeeListingService(ListingService):
    """Class-based listing API implementation"""
    filter_mapper = {
        "gdr": ("Employee.gender", generic_filters.EqualityFilter),
        "bdt": ("Employee.birth_date", generic_filters.MySqlNativeDateFormateRangeFilter),
        "fnm": ("Employee.first_name", generic_filters.StringStartsWithFilter),
        "lnm": ("Employee.last_name", generic_filters.StringEndsWithFilter),
        # a joined-table field needs a resolver, same as in the query-customisation docs
        "desg": ("Employee.Title.title", generic_filters.StringLikeFilter, lambda x: getattr(Title, x))
    }

    sort_mapper = {
        "cd": "emp_no"
    }
    default_srt_on = "Employee.emp_no"
    default_dao = EmployeeDao

    def get_listing(self):
        # same idea as the inline version, but MetaInfo is populated from self
        # rather than passed explicitly - filter/sort registration is handled implicitly,
        # and @loader.register() validates the whole definition at startup
        resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListDetails).get_response(self.MetaInfo(self))
        return resp


@app.get("/employees", response_model=ListingPage[EmployeeListDetails])
def get_employees(db: Session):
    return EmployeeListingService(read_db=db).get_listing()
```

See the [docs](https://fastapi-listing.readthedocs.io/en/latest/tutorials.html#adding-filters-to-your-listing-api)
for the full list of supported filters. You can also write your own custom filters.

## Need something the built-ins don't cover?

You can write a custom:

* Query strategy
* Filter
* Sorter
* Paginator

See the customisation section of the docs, after basics and tutorials.

A second, example-focused repo is available [here](https://github.com/danielhasan1/test-fastapi-listing/blob/master/app/router/router.py).

## Backend support

fastapi-listing ships with SQLAlchemy support by default, but nothing in the Filter/Sorter/Paginator/QueryStrategy
contract is SQLAlchemy-specific. Every one of them is written against a small `QueryContext` interface
(`fastapi_listing/context`), not a raw SQLAlchemy `Query` - `SqlAlchemyQueryContext` is just the default
implementation of it.

As proof this isn't SQLAlchemy in disguise, a **ClickHouse** backend ships as a reference implementation
(`fastapi_listing.dao.ClickHouseDao` + `fastapi_listing.context.clickhouse.ClickHouseQueryContext`) - raw
parameterized SQL via `clickhouse-driver`, no ORM at all. The same `generic_filters` classes
(`EqualityFilter`, `InDataFilter`, ...) and the default `SortingOrderStrategy`/`PaginationStrategy` work
against it completely unmodified, because they only ever talk to the `QueryContext`, never to SQLAlchemy
directly.

```bash
pip install fastapi-listing[clickhouse]
```

Canonical filters/sort/pagination cover the common case - equality/range/comparison checks on a plain
column, single-column sort, offset/limit pagination. Real queries aren't always that simple, so every
escape hatch that exists for SQLAlchemy (`context.native`) has a ClickHouse equivalent, and then some:

* **`ClickHouseQueryContext.from_raw_sql(client=..., sql=..., params=...)`** - the full bypass. Hand-build
  a query with CTEs, joins, window functions, a table function as the source, whatever the canonical `Op`
  vocabulary can't express - using whatever query-building approach you already have - and you still get
  back a `QueryContext` that canonical filters/sort/pagination can layer on top of, or that you can use
  completely as-is.
* **`HavingMixin`** - filter on an aggregated field after a `GROUP BY` (`SUM(x) > 100`), same canonical
  `Op`s, routed to `HAVING` instead of `WHERE`: `class TotalAbove(HavingMixin, DataGreaterThanFilter): pass`.
* **`order_by_raw(expression)`** - for a compound ordering rule (a tiebreak column, multiple sort keys)
  that a single `field, direction` pair can't represent.
* **`add_raw_condition(sql_template, **values)`** - a per-filter escape hatch for a backend-specific SQL
  function (a full-text search builtin, an array operator, ...) with no canonical `Op` equivalent - values
  are still bound through the driver's real parameter binding, never string-formatted into the SQL text.

Want a different ORM or database driver (Tortoise, Django ORM, raw psycopg2, pymongo, ...)? Write your own
`QueryContext` + DAO pair the same way `ClickHouseQueryContext`/`ClickHouseDao` do it - see `docs/query.rst`.
Neither SQLAlchemy nor clickhouse-driver are required to install the package; both are opt-in extras.

## Design goals

- A well-defined interface for filter, sorter, and paginator
- Dependency injection, for easy testing
- Adapters, so an existing client's query-param format doesn't have to change
- Listing APIs that stay legible as they grow, rather than accumulating branches over time

## Documentation

Full documentation: https://fastapi-listing.readthedocs.io (a work in progress)


## Feedback and questions

Feedback and questions are welcome - please [open an issue](https://github.com/danielhasan1/fastapi-listing/issues/new).
