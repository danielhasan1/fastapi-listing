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
Here we have a dao package where we will be adding all our :ref:`Dao<dao overview>` classes.
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


.. py:attribute:: ListingService.filter_mapper

    A ``dict`` containing allowed filters on the listing. ``{alias: value}`` where key should be an alias of field and value is
    a tuple.

    for example: ``{"fnm": ("Employees.first_name", filter_class)}``

    value ``"Employees.first_name"`` shows relation. ``first_name`` from model ``Employees``. This should always be unique. You could go sane defining your values
    like this which will help you when debugging. split on ``.`` happens and last value is assumed to be actual field.
    More information will be given at example level

:ref:`alias overview`?

.. py:attribute:: ListingService.sort_mapper

    A ``dict`` containing allowed sorting field on the listing. More information will be given with example


.. py:attribute:: ListingService.default_srt_on

    attribute provides field name that will be used by default to apply sort on query

.. py:attribute:: ListingService.default_srt_ord

    attributes provides sorting order that will be used to apply sorting by default allowed values are ``asc`` and ``dsc``.

.. py:attribute:: ListingService.paginate_strategy

    attribute provides pagination strategy name which will be used by listing service to apply pagination on query.
    Default strategy name ``default_paginator``


.. py:attribute::  ListingService.query_strategy

    attribute provides query strategy name, used to get base query for your listing service. Default strategy name ``default_query``


.. py:attribute:: ListingService.sorting_strategy

    attribute provides sorting strategy name, used to apply sorting on your base query. Default strategy name ``default_sorter``

.. py:attribute:: ListingService.sort_mecha

    attribute provide interceptor name.
    This attribute provides name of strategy that handles this behaviour.Default strategy name``singleton_sorter_mechanics``
    Allows only single field sorting at a time.

.. py:attribute:: ListingService.filter_mecha

    As sorting mecha this is also similar i.e., when multiple filters are applied this handle the behaviour of how filter will get applied on query.
    Default strategy name ``iterative_filter_mechanics``
    Allows multiple field filtering in iterative fashion. As to why you wanna abrupt this behaviour we will look at it later.


.. py:attribute:: ListingService.default_dao

    provides listing service :ref:`dao` class. should be created by extending ``GenericDao``
    every listing service should contain primary doa and you tell listing their primary dao by this attribtue

.. py:attribute:: ListingService.default_page_size

    defining listing service default page size. This will the page size by default.

.. py:attribute:: ListingService.feature_params_adapter

    default adapter for to resolve issue between incompatible objects. Users are advices to design their
    own adapters to support their existing client site filter/sorter/page params.


Customising your listing listing query
--------------------------------------

Most of the time you will be writing your own custom optimised queries for retrieving listing data and it is not unusual to write
multiple queries to suit the needs of any user.

A brief example could be - You have a system where users are grouped together in different roles. Each group of user are separated on
different layer of data levels so you may need to check two thing in every listing api calls
1. What role logged in user have,
2. On which data layer the user lies so only showing data associated to that user.

To tackle this situation you may wanna write different query for each layer. Some queries may look simple some may look advanced some may even corporate caching layer
and sky is the limit for complexity. If not handled well this part could easily kill your listing api performance and as complexity get greater
you could easily lose more time in doing maintenance work for existing code then adding new features.

It is just a layer of iceberg of problems and I won't be going too deep into discussing every aspect as that is out of the scope of this documentation.

Going back to the topic.

You can write N number of definitions to solve problems like this or even further divide it down to atomic level.

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



To use this your client(strategy user not the actual client like logged in user or browser) should be aware to which strategy to use in specefic
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
query strategy to show how you can plug a query strategy for each listing service at class level.
Lets say you may wanna handle query related logic completely at query strategy level then you can create a single query strategy class
write your logics (which query to load when and why) there inject that into your listing and call it a day  but for those people who wanna handle which query strategy to call at
service level and keep their query strategy classes as concrete as possible they can make use of switch which is suger coated way of saying setattr.

Some of the Benefits:
 - Write/Change your queries independently.
 - Open/Close relationship.
 - Dry Code
 - Improve readability and easy to understand classes
 - Reduces error which happen when one change breaks existing dependent flow
 - Ability to reuse existing strategies in other listing services


.. _alias overview:

Why use alias
-------------

* Avoid giving away original column names at client level. A steps towards securing and maintaining abstraction at api level.
* Shorter alias names are light weight. payload looks more friendly.
* Saves a little bit of bandwidth by saving communicating some extra characters.
* save coding time with shorter keys.






