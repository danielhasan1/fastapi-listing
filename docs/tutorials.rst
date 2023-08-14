Tutorials
=========

Preparations
------------

A simple example showing how easy it is to get started. Lets look at a little bit of context for better understanding.

**Note** First lets setup the app to use the library

Your project structure may differ, but all FastAPI related flow is similar in context.

I'll be using the following structure for this tutorial:


.. parsed-literal::

    employess
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

Lets call this app **employees**


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
        Not to be used directly as this class is missing required attributes 'model' and 'name' to be given by users.
        model class is given when we are linking a new dao class with a new model/table
        name is dao name that a user will use to invoke dao objects.
        """

        def check_pk_exist(self, id: int | str) -> bool:
            # check if id exists in linked dao table
            return self._read_db.query(self._read_db.query(self.model
                                        ).filter(self.model.id == id).exists()).scalar()


        def get_empty_query(self):
            # return empty query
            return self._read_db.query(self.model).filter(sqlalchemy.sql.false())

Dao classes

.. code-block:: python


    # each dao will be placed in their own module/files
    from fastapi_listing.dao import dao_factory

    from app.dao import ClassicDao

    class TitleDao(ClassicDao):
        name = "title"
        model = Title

    dao_factory.register_dao(TitleDao.name, TitleDao) # registering dao with app to use anywhere

    class EmployeeDao(ClassicDao):
        name = "employee"
        model = Employee

    dao_factory.register_dao(EmployeeDao.name, EmployeeDao) # registering dao with app to use anywhere

    class DeptEmpDao(ClassicDao):
        name = "deptemp"
        model = DeptEmp

    dao_factory.register_dao(DeptEmpDao.name, DeptEmpDao) # registering dao with app to use anywhere


schema
------

Response Schema (Support for pydantic 2 is added.)

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
    # anywhere in your code via single import.

    # if you have a master slave architecture
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)

    # if you have only a master database
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db)

    # if you want fastapi listing to close session when returning a response
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db, session_close_implicit=True)

router
------

Write abstract listing api routers with FastAPI Listing.
calling listing endpoint from routers

.. code-block:: python
    :emphasize-lines: 1, 5, 8

    from fastapi_listing.paginator import ListingPage
    from app.schema.response import EmployeeListingDetail
    from app.service import EmployeeListingService

    @app.get("/v1/employees", response_model=ListingPage[EmployeeListingDetail])
    def read_main(request: Request):
        resp = EmployeeListingService(request).get_listing()
        return resp

service definition is given in below.


.. _service:


Writing your very first listing API using fastapi-listing
---------------------------------------------------------

.. code-block:: python
    :emphasize-lines: 1, 6, 10, 13, 14


    from fastapi_listing import ListingService, FastapiListing, loader
    from app.dao import EmployeeDao
    from app.schema.response.employee_responses import EmployeeListDetails # optional


    @loader.register() # run system checks to validate your listing service
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao

        def get_listing(self):
            resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListDetails
                                    ).get_response(self.MetaInfo(self))
            return resp

    # that's it your very first listing api is ready to be serverd.
    #

You actually began writing your listing API here. Before this everything was vanilla FastAPI code excluding doa setup 🤠

* **loader**: A utility decorator used on startup when classes gets loaded into the memory validates the semantics also helps to identify any abnormality within
                your defined listing class.
* **ListingService**: High level base class. All Listing Service classes will extend this.
* **Attributes**: :ref:`attributes overview`
* **EmployeeListDetails**: Optional pydantic class containing required fields to render. These field will get added automatically in vanilla query.
    if you are not using pydantic then you could leave it or use list of fields.
* **get_listing**: High level function, entrypoint for listing service.
* **FastapiListing**: Low level class that you will only use as an expression which returns a result. Extending this is forbidden.

Once you runserver, hit the endpoint ``localhost:8000/v1/employees`` and you will receive a json response with page size 10 (default page size).


.. _attributes overview:

``ListingService`` high level attributes
----------------------------------------

This library is divided down to fundamental level blocks of any listing API, You can create these blocks independent from each other
inject them into your listing service and their composition will communicate implicitly so you can focus more on writing solutions and leave their communication on the core service.

.. py:currentmodule:: fastapi_listing.service.listing_main

.. _filter_mapper_label:

.. py:attribute:: ListingService.filter_mapper

    A ``dict`` containing allowed filters on the listing. ``{alias: value}`` where key should be an alias of field and value is
    a tuple. You can use actual field names in place of alias its a matter of personal preferrence 🤓

    for example: ``{"fnm": ("Employees.first_name", filter_class)}``

    value ``"Employees.first_name"`` shows relation. ``first_name`` from primary model ``Employees``.
    This should always be unique. You could go sane defining your values
    like this which will help you when debugging.

    alias/filter field will be sent in request by clients. for those who directly jumped here🤯 checkout :ref:`basics adapter layer<adapterbenefit>` first
    to see how FastAPI Listing is capable of adapting to your existing clients without any modification.

For customising the behaviour you can check out customisation section ✏️.

:ref:`alias overview`?

.. py:attribute:: ListingService.sort_mapper

    A ``dict`` containing allowed sorting on the listing.

    for example: ``{"empno": "Employees.emp_no"}``

    sorter alias/fields will be sent in request by clients and you know FastAPI Listing can :ref:`adapt<adapterbenefit>` to them.


.. py:attribute:: ListingService.default_srt_on

    attribute provides field name used to sort listing item by default

.. py:attribute:: ListingService.default_srt_ord

    attributes provides sorting order, allowed ``asc`` and ``dsc`` 📝.

.. py:attribute:: ListingService.paginate_strategy

    attribute provides pagination strategy name used by listing service to apply pagination on query.
    Default strategy - ``default_paginator``


.. py:attribute::  ListingService.query_strategy

    attribute provides query strategy name, used to get base query for your listing service.
    Default strategy - ``default_query``


.. py:attribute:: ListingService.sorting_strategy

    attribute provides sorting strategy name, used to apply sorting on your base query.
    Default strategy - ``default_sorter``

.. py:attribute:: ListingService.sort_mecha

    attribute provides interceptor name. :ref:`interceptors<intereptorbasics>` ❓️
    Default interceptor - ``indi_sorter_interceptor``

.. py:attribute:: ListingService.filter_mecha

    attribute provides interceptor name. :ref:`interceptors<intereptorbasics>` ❓️
    Default interceptor -  ``iterative_filter_interceptor``


.. py:attribute:: ListingService.default_dao

    provides listing service :ref:`dao` class.
    every listing service should contain one primary doa only. You can use multiple dao/sqlalchemy models/tables in defintion via dao_factory.

.. py:attribute:: ListingService.default_page_size

    default number of items in a single page.

.. _adapter_attr:

.. py:attribute:: ListingService.feature_params_adapter

    default adapter to resolve issue between incompatible objects. Users are advices to design their
    own adapters to support their existing remote client site filter/sorter/page params. :ref:`adapters<adapterbenefit>` ❓️

