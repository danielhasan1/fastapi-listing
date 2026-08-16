Tutorials
=========

Preparations
------------

A walkthrough of building a listing API end to end. Your project layout may differ, but the FastAPI
wiring is the same regardless.

This tutorial uses the following structure:

.. parsed-literal::

    employees
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

Call this app **employees**.


models
------

Model classes:

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

A local ``dao`` package holds every :ref:`DAO <dao overview>` class. It's also common to keep a small
package of generic, reusable DAO helpers - here, ``dao_generics.py``:

.. code-block:: python

    import sqlalchemy

    from fastapi_listing.dao import GenericDao
    from fastapi_listing.context.sqlalchemy import SqlAlchemyQueryContext


    class ClassicDao(GenericDao):  # noqa
        """
        Not meant to be used directly - it's missing the required 'model' and 'name'
        attributes, which a concrete subclass provides when binding to a model/table.
        """

        def check_pk_exist(self, id: int | str) -> bool:
            return self._read_db.query(
                self._read_db.query(self.model).filter(self.model.id == id).exists()
            ).scalar()

        def get_empty_query(self) -> SqlAlchemyQueryContext:
            return SqlAlchemyQueryContext(self._read_db.query(self.model).filter(sqlalchemy.sql.false()))

Concrete DAO classes, one per model, each in their own module:

.. code-block:: python

    from fastapi_listing.dao import dao_factory

    from app.dao import ClassicDao

    class TitleDao(ClassicDao):
        name = "title"
        model = Title

    dao_factory.register_dao(TitleDao.name, TitleDao)  # makes the DAO usable anywhere via dao_factory

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

Response schema (Pydantic v2 is supported):

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

Add the session-binding middleware in your main file:

.. code-block:: python
    :emphasize-lines: 17

    def get_db() -> Session:
        """
        Stand-in for a sessionmaker. Use whatever gives you a Session -
        fastapi-sqlalchemy or your own factory both work the same way here.
        :return: Session
        """
        engine = create_engine("mysql://root:123456@127.0.0.1:3307/employees", pool_pre_ping=1)
        sess = Session(bind=engine)
        return sess


    app = FastAPI()
    # DaoSessionBinderMiddleware makes a registered dao usable anywhere via a
    # single import, without threading a session through every function call.

    # if you have a primary/replica architecture:
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)

    # if you have a single database:
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db)

    # if you want FastAPI Listing to close the session before returning the response:
    app.add_middleware(DaoSessionBinderMiddleware, master=get_db, session_close_implicit=True)

router
------

Write listing endpoint routers with FastAPI Listing - calling the listing endpoint from a router looks
like this:

.. code-block:: python
    :emphasize-lines: 1, 5, 8

    from fastapi_listing.paginator import ListingPage
    from app.schema.response import EmployeeListingDetail
    from app.service import EmployeeListingService

    @app.get("/v1/employees", response_model=ListingPage[EmployeeListingDetail])
    def read_main(request: Request):
        resp = EmployeeListingService(request).get_listing()
        return resp

The service definition follows below.


.. _service:


Writing your first listing API with FastAPI Listing
-----------------------------------------------------

.. code-block:: python
    :emphasize-lines: 1, 6, 10, 13, 14


    from fastapi_listing import ListingService, FastapiListing, loader
    from app.dao import EmployeeDao
    from app.schema.response.employee_responses import EmployeeListDetails  # optional


    @loader.register()  # validates the listing service's semantics at startup
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao

        def get_listing(self):
            resp = FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListDetails
                                    ).get_response(self.MetaInfo(self))
            return resp

    # that's it - the first listing API is ready to serve.

Everything before this point was plain FastAPI/DAO setup; this is where the listing API itself begins.

* **loader**: a startup-time decorator that validates a listing service's semantics and flags mistakes early, rather than at request time.
* **ListingService**: the base class every listing service extends.
* **Attributes**: see :ref:`attributes overview`.
* **EmployeeListDetails**: an optional Pydantic class listing the fields to render; these are added to the query automatically. Without Pydantic, pass a plain list of field names instead.
* **get_listing**: the entry point for the listing service.
* **FastapiListing**: a low-level class used as an expression that returns a result - not meant to be subclassed.

Start the server and hit ``localhost:8000/v1/employees`` to get a JSON response with 10 items (the
default page size).


.. _attributes overview:

``ListingService`` high level attributes
------------------------------------------

Each of these blocks - filter, sort, pagination, query - is independent and composes implicitly through
the core service, so you can focus on the logic of each rather than how they're wired together.

.. py:currentmodule:: fastapi_listing.service.listing_main

.. _filter_mapper_label:

.. py:attribute:: ListingService.filter_mapper

    A ``dict`` of allowed filters: ``{alias: value}``, where the key is an alias for the field (or the
    field name itself, if you'd rather not alias it) and the value is a tuple.

    Example: ``{"fnm": ("Employees.first_name", filter_class)}``

    ``"Employees.first_name"`` shows the relation - ``first_name`` on the primary model, ``Employees``.
    This value should always be unique; keeping it descriptive like this also helps when debugging.

    The alias is what the client sends. If you're adapting an existing client's parameters rather than
    starting fresh, see :ref:`the adapter layer <adapterbenefit>` first.

See :ref:`alias overview` for why aliasing is worth doing in the first place.

.. py:attribute:: ListingService.sort_mapper

    A ``dict`` of allowed sort fields.

    Example: ``{"empno": "Employees.emp_no"}``

    As with filters, sort aliases can be adapted to an existing client via :ref:`the adapter layer <adapterbenefit>`.


.. py:attribute:: ListingService.default_srt_on

    The field to sort by when the request specifies no sort parameter.

.. py:attribute:: ListingService.default_srt_ord

    The default sort order: ``asc`` or ``dsc``.

.. py:attribute:: ListingService.paginate_strategy

    The pagination strategy name.
    Default: ``default_paginator``.


.. py:attribute::  ListingService.query_strategy

    The query strategy name, used to build the base query.
    Default: ``default_query``.


.. py:attribute:: ListingService.sorting_strategy

    The sort strategy name, used to apply sorting to the base query.
    Default: ``default_sorter``.

.. py:attribute:: ListingService.sort_mecha

    The sort interceptor name - see :ref:`interceptors <intereptorbasics>`.
    Default: ``indi_sorter_interceptor``.

.. py:attribute:: ListingService.filter_mecha

    The filter interceptor name - see :ref:`interceptors <intereptorbasics>`.
    Default: ``iterative_filter_interceptor``.


.. py:attribute:: ListingService.default_dao

    The listing service's :ref:`DAO <dao overview>` class. Each listing service has exactly one primary
    DAO, though a DAO can reference other models/tables via ``dao_factory`` when needed.

.. py:attribute:: ListingService.default_page_size

    The default number of items per page.

.. _adapter_attr:

.. py:attribute:: ListingService.feature_params_adapter

    The adapter used to reconcile an existing client's filter/sort/pagination parameter shape with
    FastAPI Listing's own. Write your own to support your client's existing format - see
    :ref:`the adapter layer <adapterbenefit>`.
