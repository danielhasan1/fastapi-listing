Tutorials
=========

Preparations
------------

A simple example showing how easy it is to get started. Lets look at a little bit of context for better understanding.

**Note** First lets setup the app to use the library

Your project structure may differ, but all FastAPI related flow is similar in context.

I'll be using the following structure for this tutorial:


.. parsed-literal::

    customer
    \|-- app
    |   \|-- __init__.py
    |   \|-- :ref:`dao`
    |   |   \|-- __init__.py
    |   |   \|-- title_dao.py
    |   |   \|-- dept_emp_dao.py
    |   |   \|-- generics
    |   |   |   \|-- __init__.py
    |   |   |   \`-- dao_generics.py
    |   |   \|-- :ref:`models`
    |   |   |   \|-- __init__.py
    |   |   |   \|-- title.py
    |   |   |   \|-- dept_emp.py
    |   |   |   \`-- employee.py
    |   |   \`-- employee_dao.py
    |   \|-- :ref:`router`
    |   |   \|-- __init__.py
    |   |   \`-- employee_router.py
    |   \|-- :ref:`schema`
    |   |   \|-- __init__.py
    |   |   \|-- request
    |   |   |   \|-- __init__.py
    |   |   |   \|-- title_requests.py
    |   |   |   \`-- employee_requests.py
    |   |   \`-- response
    |   |       \|-- __init__.py
    |   |       \|-- title_responses.py
    |   |       \`-- employee_responses.py
    |   \`-- :ref:`service<service>`
    |       \|-- __init__.py
    |       \|-- strategies
    |       \`-- employee_service.py
    \|-- main.py
    \`-- requirements.txt

Lets call this app **employee**


models
------

model classes

.. code-block:: python


    class Employee(Base):
        __tablename__ = 'employees'

        emp_no = Column(Integer, primary_key=True)
        birth_date = Column(Date, nullable=False)
        first_name = Column(String(14), nullable=False)
        last_name = Column(String(16), nullable=False)
        gender = Column(Enum('M', 'F'), nullable=False)
        hire_date = Column(Date, nullable=False)


    class DeptEmp(Base):
        __tablename__ = 'dept_emp'

        emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
        dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
        from_date = Column(Date, nullable=False)
        to_date = Column(Date, nullable=False)

        department = relationship('Department')
        employee = relationship('Employee')

    class Title(Base):
        __tablename__ = 'titles'

        emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
        title = Column(String(50), primary_key=True, nullable=False)
        from_date = Column(Date, primary_key=True, nullable=False)
        to_date = Column(Date)

        employee = relationship('Employee')

Dao
---
Here we have a local dao package where we will be adding all our :ref:`Dao<dao overview>` classes.
I've additionally added a package to keep generic methods for common use, e.g. ``dao_generics.py`` file which looks something
like this

.. code-block:: python


    from fastapi_listing.dao import GenericDao


    class ClassicDao(GenericDao):  # noqa
        """
        Not to be used directly as this class is missing an abstract property model.
        model is given when we are registering a new dao class under a new model/table
        this is a collection of of helper properties that can be used anywhere.
        """

        def check_pk_exist(self, id: int | str) -> bool:
            return self._read_db.query(self._read_db.query(self.model
                                        ).filter(self.model.id == id).exists()).scalar()


        def get_empty_query(self):
            return self._read_db.query(self.model).filter(sqlalchemy.sql.false())

Dao classes

.. code-block:: python


    # each dao will be placed in their own module/files
    from fastapi_listing.dao import dao_factory

    from app.dao import ClassicDao

    class TitleDao(ClassicDao):
        name = "title"
        model = Title

    dao_factory.register_dao(TitleDao.name, TitleDao)

    class EmployeeDao(ClassicDao):
        name = "employee"
        model = Employee

    dao_factory.register_dao(EmployeeDao.name, EmployeeDao)

    class DeptEmpDao(ClassicDao):
        name = "deptemp"
        model = DeptEmp

    dao_factory.register_dao(DeptEmpDao.name, DeptEmpDao)


schema
------

Response Schema

.. code-block:: python


    class GenderEnum(enum.Enum):
        MALE = "M"
        FEMALE = "F"

    class EmployeeListDetails(BaseModel):
        emp_no: int = Field(alias="empid", title="Employee ID")
        birth_date: date = Field(alias="bdt", title="Birth Date")
        first_name: str = Field(alias="fnm", title="First Name")
        last_name: str = Field(alias="lnm", title="Last Name")
        gender: GenderEnum = Field(alias="gdr", title="Gender")
        hire_date: date = Field(alias="hdt", title="Hiring Date")

        class Config:
            orm_mode = True
            allow_population_by_field_name = True

    class EmployeeListingResponse(BaseModel):
        data: List[EmployeeListDetails] = []
        currentPageSize: int
        currentPageNumber: int
        hasNext: bool
        totalCount: int


main
----
Add middleware at main file

.. code-block:: python
    :emphasize-lines: 17

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
    # fastapi-listing middleware offering anywhere dao usage policy. Just like anywhere door use sessions and dao
    # anywhere in your code.
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)

router
------

Write abstract listing api routers with FastAPI Listing.
calling listing endpoint from routers

.. code-block:: python
    :emphasize-lines: 4

    @app.get("/v1/employees", response_model=EmployeeListingResponse)
    def read_main(request: Request):
        # The service definition will is given below
        resp = EmployeeListingService(request).get_listing()
        return resp




.. _service:


Writing your very first listing API using fastapi-listing.
----------------------------------------------------------
Service layer where one write all their business logics


Creating your first **listing api** that will be called from router to return a listing response.

.. code-block:: python
    :emphasize-lines: 1, 7, 8, 10, 11, 13, 14, 15


    from fastapi_listing import ListingService, FastapiListing
    from fastapi_listing import loader # setup utility called when classes are loaded
    from app.dao import EmployeeDao
    from app.schema.response.employee_responses import EmployeeListDetails # optional


    @loader.register()
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao

        def get_listing(self):
            resp = FastapiListing(self.request, self.dao, EmployeeListDetails
                                    ).get_response(self.MetaInfo(self))
            return resp

    # that's it your very first listing api is ready to be serverd.

You actually began writing your listing api here at listing service level. Before this everything was vanilla FastAPI code.

* **loader**: A utility decorator used on startup when classes gets loaded into the memory validates the semantics also helps to identify any abnormality within
                your defined listing class.
* **ListingService**: High level base class. All Listing Service classes will extend this.
* **Attributes**: :ref:`attributes overview`
* **EmployeeListDetails**: Optional pydantic class containing required fields to render. These field will get added automatically in vanilla query.
    if you are not using pydantic then you could leave it.
* **get_listing**: High level function, entrypoint for listing service.
* **FastapiListing**: Low level class that you will only use as an expression which returns a result. Never extend it just use it as an expression like operators.

Once you runserver, hit the endpoint ``localhost:8000/v1/employees`` and you will receive a json response with page size 10 (default page size).


.. _attributes overview:

``ListingService`` high level attributes
----------------------------------------

I've divided down the fundamental blocks of any listing service, You can create these blocks independent from each other
inject them into your listing service and their composition will communicate implicitly so you can focus more on writing solutions and leave their communication on the core service.

.. py:currentmodule:: fastapi_listing.service.listing_main

.. _filter_mapper_label:

.. py:attribute:: ListingService.filter_mapper

    A ``dict`` containing allowed filters on the listing. ``{alias: value}`` where key should be an alias of field and value is
    a tuple.

    for example: ``{"fnm": ("Employees.first_name", filter_class)}``

    value ``"Employees.first_name"`` shows relation. ``first_name`` from primary model ``Employees``.
    This should always be unique. You could go sane defining your values
    like this which will help you when debugging. split on ``.`` happens and last value is assumed to be actual field.
    More information will be given at example level.

:ref:`alias overview`?

.. py:attribute:: ListingService.sort_mapper

    A ``dict`` containing allowed sorting field on the listing. More information will be given with example


.. py:attribute:: ListingService.default_srt_on

    attribute provides field name that will be used by default to apply sort on query

.. py:attribute:: ListingService.default_srt_ord

    attributes provides sorting order that will be used to apply sorting by default allowed values are ``asc`` and ``dsc``. 📝

.. py:attribute:: ListingService.paginate_strategy

    attribute provides pagination strategy name which will be used by listing service to apply pagination on query.
    Default strategy name ``default_paginator``


.. py:attribute::  ListingService.query_strategy

    attribute provides query strategy name, used to get base query for your listing service. Default strategy name ``default_query``


.. py:attribute:: ListingService.sorting_strategy

    attribute provides sorting strategy name, used to apply sorting on your base query. Default strategy name ``default_sorter``

.. py:attribute:: ListingService.sort_mecha

    attribute provide interceptor name.
    This attribute provides name of strategy that handles this behaviour.Default strategy name``indi_sorter_interceptor``
    Allows only single field sorting at a time.

.. py:attribute:: ListingService.filter_mecha

    As sorting mecha this is also similar i.e., when multiple filters are applied this handle the behaviour of how filter will get applied on query.
    Default strategy name ``iterative_filter_interceptor``-
    Allows multiple field filtering in iterative fashion. As to why you wanna abrupt this behaviour we will learn this when we learn to write our filters. :ref:`learnfilters`


.. py:attribute:: ListingService.default_dao

    provides listing service :ref:`dao` class. should be created by extending ``GenericDao``
    every listing service should contain primary doa and you tell listing their primary dao by this attribute

.. py:attribute:: ListingService.default_page_size

    defining listing service default page size. This will the page size by default.

.. _adapter_attr:

.. py:attribute:: ListingService.feature_params_adapter

    default adapter to resolve issue between incompatible objects. Users are advices to design their
    own adapters to support their existing remote client site filter/sorter/page params.


Customising your listing  query
-------------------------------

Most of the time you will be writing your own custom optimised queries for retrieving listing data and it is not unusual to write
multiple queries to suit the needs of any logged in user to your service.

A brief example could be - You have a system where users are grouped together in different roles. Each group of user are separated on
different layer of data levels so you may need to check two thing in every listing api calls
1. What role logged in user have,
2. On which data layer the user lies so only showing data associated to that user.

To tackle this situation you may wanna write different query for each layer. Some queries may look simple some may look advanced some may even corporate caching layer
and sky is the limit for complexity. If not handled well this part could easily kill your listing api performance and as complexity get greater
you could easily lose more time in doing maintenance work for existing code than adding new penny features which could cost you more time.

It is just a layer of iceberg of problems and I won't be going too deep into discussing every aspect as that is out of the scope of this documentation.

Going back to the topic.

You can write N number of definitions to solve problems like this or even further divide it down to atomic level and just plug them or attach them at runtime
via writing a custom listing client(a fancy word of saying writing down your own solution to switch between different strategies)

Lets say you have a dept manager table

.. code-block:: python


    class DeptManager(Base):
        __tablename__ = 'dept_manager'

        emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
        dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False,
                         index=True)
        from_date = Column(Date, nullable=False)
        to_date = Column(Date, nullable=False)

        department = relationship('Department')
        employee = relationship('Employee')


Whenever department managers logs into the app they should only see employees who are associated to them (engineering department manager should only see engineering staff)

Writing your own query strategy

.. code-block:: python


    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory


    class DepartmentWiseEmployeesQuery(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                      extra_context: dict = None) -> SqlAlchemyQuery:
            # as request and dao args are self explanatory
            # extra_context is a chained variable that can carry contextual data from one place
            # to another place. extremely helpful when passing args from router or client.
            dept_no: str = dept_no # assuming we found dept no of logged in manager
            return dao.get_employees_by_dept(dept_no) # method defined in dao class

    # it is important to register your strategy with factory for use.
    strategy_factory.register("<whatever name you choose>", DepartmentWiseEmployeesQuery)

.. _dept_emp_q_stg:

Add your new listing query to employee dao

.. code-block:: python


    from sqlalchemy.orm import Query

    class EmployeeDao(ClassicDao):
        name = "employee"
        model = Employee

        def get_employees_by_dept(self, dept_no: str) -> Query:
            # assuming we have one to one mapping and we are passing manager department here
            query = self._read_db.query(Employee
                                        ).join(DeptEmp, Employee.emp_no == DeptEmp.emp_no
                                        ).filter(DeptEmp.dept_no == dept_no)
            return query



To use this your listing client(strategy user not the actual client like logged in user or browser) should be aware to which strategy to use in specific
condition

.. code-block:: python
    :emphasize-lines: 9

    @loader.register()
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        # query_strategy = "default_query"
        def get_listing(self):
            if user == manager: # imaginary conditions
                self.switch("query_strategy","<whatever name we choose>") # switch strategy on the fly on object/request level

            resp = FastapiListing(self.request, self.dao, EmployeeListDetails
                                    ).get_response(self.MetaInfo(self))
            return resp

In above example I have decided to make a switch for query strategy at runtime. I have also intentionally commented the default
query strategy to show how you can plug a query strategy for each listing service at class level. So whenever a department manager logs in query strategy will be
switched to fetch relative data and whenever other user logs in they will see global data because you have a default query strategy placed as well.
Lets say you may wanna handle query related logic completely at query strategy level then you can create a single query strategy class
write your logics (which query to load when and why) there inject that into your listing and call it a day  but for those people who wanna handle which query strategy to call at
service level and keep their query strategy classes as atomic as possible they can make use of switch which is suger coated way of saying setattr.
Personally I like to write atomic level code that is each block is responsible for one thing so whenever someone is reading/writing writing a new revision.
they could always write their own block and call them and if something goes wrong they could very fast switch to the older version look for possible issues and
then switch back to the new revision.

Also helps when you are refactoring your code, this shows all existing code and you will see how the project transformed/took turn for better or for worse.

I would like to say this additionally that this completely depends on your software design skills. Metaphorically One can design a master piece with
provided apparatus or one can create a normy art with the same apparatus.

Summarised Benefits:
 - Write/Change your queries independently❤️
 - Open/Close relationship😍
 - Dry Code
 - Improve readability and easy to understand classes😍
 - Reduces error which happen when one change breaks existing dependent flow😎
 - Ability to reuse existing strategies in other listing services😎
 - Ability to read software alterations with ease in future😎
 - Ability to review the change by each development cycle without digging into git history😎

.. _learnfilters:

Adding Filters to your listing API
----------------------------------

The most interesting part of a listing that becomes the most hated part of any listing super easily.

Starting with an easy request.

Adding a filter that will filter your employee listing on basis of  ``gender``.

.. code-block:: python
    :emphasize-lines: 1, 7

    from fastapi_listing.filters import generic_filters


    @loader.register()
    class EmployeeListingService(ListingService):

        filter_mapper = {
            "gdr": ("Employee.gender", generic_filters.EqualityFilter),
        }

        # rest of the definition is going to be same no change required.

In above example we have imported a module ``generic_filters`` which holds some of the very commonly used query filters supported by FastAPI Listing.
These are highly reusable and support a cross model in place hook when you may wanna provide secondary model field.
There are a bunch of filters out of the box to speed up your regular listing API development.😉



.. list-table::
   :widths: auto

   * - ``EqualityFilter``
     - equality filter ``a == b``
   * - ``InEqualityFilter``
     - inequality filter ``a != b``
   * - ``InDataFilter``
     - ``in`` filter ``a in (b)``
   * - ``BetweenUnixMilliSecDateFilter``
     - best way to avoid conflict between date formate awareness. deal in unix timestamp. range filter ``between(start,end)``
   * - ``StringStartsWithFilter``
     - like filter ``a like b%``
   * - ``StringEndsWithFilter``
     - like filter ``a like %b``
   * - ``StringContainsFilter``
     - contains substring filter ``a like %b%``. recommended use on only small tables
   * - ``StringLikeFilter``
     - string equality filter ``a like b``
   * - ``DataGreaterThanFilter``
     - greater than filter ``a > b``
   * - ``DataGreaterThanEqualToFilter``
     - greater than equal to filter ``a >= b``
   * - ``DataLessThanFilter``
     - less than filter a < b
   * - ``DataLessThanEqualToFilter``
     - less than equal to filter a <= b
   * - ``DataGropByElementFilter``
     - aggregation filter ``a group by b``
   * - ``DataDistinctByElementFilter``
     - distinct data filter ``distinct a``
   * - ``HasFieldValue``
     - has field filter ``a is null`` or ``a is not null``
   * - ``MySqlNativeDateFormateRangeFilter``
     - native date formate range filter between(a,b)


I hope you still remember :ref:`filter_mapper <filter_mapper_label>`

Each item of this mapping dict has 3 key components.

1. the key itself which will be sent in remote client request.
2. The tuple
    * first item is ``model.field`` -> Field associated to primary table. The filter will be applied on it.
    * second item is your filter class definition.

And that's it you have successfully implemented your first filter.


Several benefits of having an alias over your actual fields as shown in the above dict key.
1. You will never expose your actual field name to the remote client which help to secure your service.
2. You will have a more cleaner looking request urls which will only make sense to software developers.
3. It will trim out the extra information exposing from urls.

How FastAPI Listing reads filter params:

* when you have a single value filter - ``[{"field": "alias<(filter mapper dict key)>", "value":{"search":<whatever remote client chose to search>}}]`` 📝
* when you have multi value filter - ``[{"field": "alias<(filter mapper dict key)>", "value":{"list":<whatever remote client chose to search in list>}}]`` 📝
* when you have a range value filter - ``[{"field": "alias<(fileter mapper dict key)>", "value":{"start":<whatever remote client chose to search>, "end":<whatever remote client chose to search>}}]`` 📝

**If you have an existing running service that means you already have running remote client setup that will be sending different named query params for filter, then
use the :ref:`adapter` to make your existing listing service adapt to your existing code.**


Customising your filters
^^^^^^^^^^^^^^^^^^^^^^^^

Using secondary model field. Lets say you wanna use a field from ``DeptEmp`` model. If you give the write your filter like this

.. code-block:: python

    filter_mapper = {
        "gdr": ("Employee.dept_no", generic_filters.EqualityFilter),
    }

it will raise an attribute error which is expected as your primary model doesnt have this field.
We have a rule to only allow a primary model plugged to our listing service.

To allow passing secondary model field

.. code-block:: python
    :emphasize-lines: 2

    filter_mapper = {
        "dpt": ("Employee.DeptEmp.dept_no", generic_filters.EqualityFilter, lambda x: getattr(DeptEmp, x))
    }

Lets see what extra we have in our tuple above.

We have an extra lambda definition which tells what model field to use when this filter gets applied.
As to why I chained two model names ``Employee.DeptEmp.dept_no``?

There is a filter factory which centrally encapsulates all application logic. It works on unique field names(So you can't provide duplicate names).
the **alias(filter mapper dict key)** could be same for multiple listing services and multiple database schema could contain same field names
but any database asks you to provide unique schema(table) name similarly we register the filter under `schema.field` name to reduce for users to always coming
up with random unique names.
Chaining the name like this shows a clear relation that from ``Employee`` to ``DeptEmp`` where field is ``dept_no``.
Though you can argue with it and still choose a different way of adding your filter field. Just make sure it is understandable.

Note that if we use filter with this query strategy :ref:`dept emp query strategy <dept_emp_q_stg>` then only this would work. becuase our base query is aware of
``DeptEmp``.

Writing a custom filter
^^^^^^^^^^^^^^^^^^^^^^^

You wanna write your own filter because FastAPI Listing default filters were unable to fulfill your use case 🥹.

Its easy to do as well. You wanna write a filter which does a full name scan combining first_name and last_name columns.

.. code-block:: python
    :emphasize-lines: 2, 4, 6

    from fastapi_listing.filters import generic_filters
    from fastapi_listing.dao import dao_factory

    class FullNameFilter(generic_filters.CommonFilterImpl):

        def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
            # field is not necessary here as this is a custom filter and user have full control over its implementation
            if value:
                emp_dao: EmployeeDao = dao_factory.create("employee", replica=True)
                emp_ids: list[int] = emp_dao.get_emp_ids_contain_full_name(value.get("search"))
                query = query.filter(self.dao.model.emp_no.in_(emp_ids))
            return query

As you can see in above filter class we are inheriting from a class which is a part of our ``generic_filters`` module.
In our filter class we have a single filter method with fixed signature. you will receive your filter value as a dict.
We have also used **dao factory**  which allows us to use anywhere dao policy.
You basically filter your query and return it.
And just like that voila your custom filter is ready. No need to think how you will call it, this will be handled implicitly by filter mechanics(interceptor).

Why do we need an interceptor? Just bear with this example to have an idea of when you may wanna use or write your own interceptor.

Lets say you have a listing of products and a mapping table where products are mapped to some groups and each group belongs to a bigger group.

Your mapping table looks like this

.. code-block:: sql

    id | product_id | group_id | sub_group_id


You added filters for group sub group and product on your listing. You wrote your custom filters to either apply **lazy join** or resolve mapping data
and then apply the filter. So when:

* A user applies Group filter - Your custom Group Filter gets called.
* A user applies Sub Group filter - Your custom SubGroup Filter gets called with above Group Filter because user hasn't removed above filter.
* A user applies Product filter with above two filters Your Product filter gets called with maybe with existing ``generic_filters.EqualityFilter`` Filter.

Group -> Sub Group -> Product

As the default interceptor runs in an iterative fashion which applies filter one by one you may end up getting different results. Why? lets see:

You may try to find id of products mapped to Group A and applies filter on these ids. Perfect ✅

``select product_id from mapping where group_id = 'A';``

and then feed these product_id into your filter via ``in`` query.

On application of second filter you will repeat above process to find product ids and apply the filter again but wait will you receive sane results? I doubt it. ❌

``select product_id from mapping where sub_group_id = "A_a";``

First your Group Filter is called. It returned product_ids. Then your Sub Group Filter is called and it may return different product_ids
again you will feed these product_ids into your filter via ``in`` query. To avoid this you could create an advanced filter which is combination of both.
Create a custom filter where you could find product_ids with below query

``select product from mapping where group_id = 'A' and sub_group_id = 'A_a';`` ✅

This will give you accurate product_ids. Once you have a custom filter you could detect if these two filters are applied together
and modify their application by combining these two into one.

Hope this gives you a more clear picture of situations where filter interceptor could play a significance role in reducing code complexity and
providing a more cleaner approach towards writing your code.

I've faced situations like this in some system and to resolve such situation interceptor could be a big help.

Adding Sorters to your listing API
----------------------------------

This part is simple. As we leave it in the hand of db to sort our data in its own cluster FastAPI listing provides a strategy class
to apply sort on our listing query.

.. code-block:: python
    :emphasize-lines: 3, 4, 5

    @loader.register()
    class EmployeeListingService(ListingService):
        default_srt_ord: str = "dsc" # change the value to asc if you want ascending order. default value is dsc for latest data.
        default_srt_on = "Employee.emp_no" # default sorting field used when no loading listing with no sorting parameter.
        sort_mapper = {
            "empid": "emp_no",
        }

``sort_mapper`` is similar to ``filter_mapper`` where ``empid`` is what remote client sends and ``emp_no`` is what gets used to sort our dataset.
it is a collection of allowed sorting parameters.

If using primary model you could use it just like shown above.

Or if sorting is implemented on joined table field and like filter mapper

.. code-block:: python
    :emphasize-lines: 2

    sort_mapper = {
        "deptno": ("dept_no", lambda x: getattr(DeptEmp, x))
    }

like filter mapper there is no central sorter factory. As we leave the heavy lifting to DB. so there is no need to provide unique field names for registration purpose.
Although its better to use ``model.field`` convention like we used in filter mapper to keep the similarity.

Just like filter interceptor you also have an option of sorter interceptor where you could interrupt the default behaviour of applying sort on your query
and customise how you may wanna apply multi field sorting on your query.

How FastAPI Listing reads sorter params:

``[{"field":"alias", "type":"asc"}]`` or ``[{"field":"alias", "type":"dsc"}]`` 📝

**If you have an existing running service that means you already have running remote client setup that will be sending different named query params for filter, then
use the** :ref:`adapter <adapter_attr>` **to make your existing listing service adapt to your existing code.**


Customising Paginator Strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have a default pagination class. Which handles slicing of our data into pages with variable size. The provided pagination ``class``
is simple and gets the work done. If you wanna write your own efficient paginating strategy for huge tables or any other use case
you could write one by extending existing base or abstract paginating strategy ``class``.

For example you may wanna implement a paginating strategy which works on range ids for huge tables or only `previous` `next` pagination strategy and avoid
any count query.


.. code-block:: python
    :emphasize-lines: 3, 4

    @loader.register()
    class EmployeeListingService(ListingService):
        paginate_strategy: str = "default_paginator"
        default_page_size: int = 10 # default page size modify this to change default page size.



.. _alias overview:

Why use alias
-------------

* Avoid giving away original column names at client level. A steps towards securing and maintaining abstraction at api level.
* Shorter alias names are light weight. payload looks more friendly.
* Saves a little bit of bandwidth by saving communicating some extra characters.
* save coding time with shorter keys.






