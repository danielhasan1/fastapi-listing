Tutorials
=========

Preparations
------------

A simple example showing how easy it is to get started. Lets look at a little bit of context for better understanding.

**Note** this is all related to fastapi, your structure may differ, and all fastapi related flow will most of the time carry contextual code.

I'll be using the following structure for this tutorial:


.. parsed-literal::

    customer
    \|-- app
    |   \|-- __init__.py
    |   \|-- :ref:`dao`
    |   |   \|-- __init__.py
    |   |   \|-- address_dao.py
    |   |   \|-- generics
    |   |   |   \|-- __init__.py
    |   |   |   \`-- dao_generics.py
    |   |   \|-- :ref:`models`
    |   |   |   \|-- __init__.py
    |   |   |   \|-- address.py
    |   |   |   \`-- user.py
    |   |   \`-- user_dao.py
    |   \|-- :ref:`router`
    |   |   \|-- __init__.py
    |   |   \`-- user_router.py
    |   \|-- :ref:`schema`
    |   |   \|-- __init__.py
    |   |   \|-- request
    |   |   |   \|-- __init__.py
    |   |   |   \|-- address_requests.py
    |   |   |   \`-- user_requests.py
    |   |   \`-- response
    |   |       \|-- __init__.py
    |   |       \|-- address_responses.py
    |   |       \`-- user_responses.py
    |   \`-- :ref:`service<service>`
    |       \|-- __init__.py
    |       \|-- strategies
    |       \`-- user_service.py
    \|-- main.py
    \`-- requirements.txt

Lets call this app **customer**


models
------

model classes::

    # sample user.py

    class User(Base):
        __tablename__ = 'users'

        id = Column(INTEGER, primary_key=True)
        first_name = Column(VARCHAR(255), nullable=False)
        last_name = Column(VARCHAR(255))
        email = Column(VARCHAR(255), unique=True) # unique
        company = Column(VARCHAR(100))

    class AddressType(enum.Enum):
        company_address = 1
        business_address = 2
        other = 3

    # sample address.py

    class Address(Base):
        __tablename__ = 'addresses'

        id = Column(INTEGER, primary_key=True)
        line1 = Column(VARCHAR(255))
        line2 = Column(VARCHAR(255))
        city = Column(VARCHAR(255), nullable=False)
        state = Column(VARCHAR(255), nullable=False, index=True)
        country = Column(VARCHAR(255), nullable=False)
        pincode = Column(Integer, nullable=False)
        type = Column(ENUM(AddressType))
        user_id = Column(ForeignKey('users.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)


Dao
---
Here we have a dao package where we will be adding all our :ref:`Dao<dao overview>` classes.
I've additionally added a package in where I like to keep all my generic solutions, for now I've added ``dao_generics.py`` file which looks something
like this::

    from fastapi_listing.dao import GenericDao


    class ClassicDaoFeatures(GenericDao):  # noqa
        """
        Not to be used directly as this class is missing an abstract property model.
        model is given when we are registering a new dao class under a new model/table
        this is a collection of of helper properties that can be used anywhere.
        """

        def check_pk_exist(self, id: int | str) -> bool:
            return self._read_db.query(self._read_db.query(self.model).filter(self.model.id == id).exists()).scalar()


        def get_empty_query(self):
            return self._read_db.query(self.model).filter(sqlalchemy.sql.false())

Dao classes::

    # address_dao.py
    from app.dao.generics import ClassicDaoFeatures
    from app.dao.model import Address


    class AddressDao(ClassicDaoFeatures):

        model = Address


    # user_dao.py
    from app.dao.generics import ClassicDaoFeatures
    from app.dao.model import User

    class UserDao(ClassicDaoFeatures):

        model = User


schema
------

Response Schema::

    # user_responses.py

    class UserListingDetails(BaseModel):
        id: int
        first_name: str
        last_name: str
        email: str

    class UserListingResponse(BaseModel):
        data: list[UserListingDetails]
        hasNext: bool
        currentPageNumber: int
        currentPageSize: int
        totalCount: int


router
------

calling listing endpoint from routers::

    # user_router.py
    from fastapi import Request, APIRouter, Depends
    # service defined in service layer

    # service defined at service layer
    from app.service import UserListingService


    user_router_v1 = APIRouter(
        prefix="/v1/users", tags=["users"]
    )
    def get_read_db_session():
        # sample method to return a sess
        return Session

    @user_router_v1.get("", response_model=UserListingDetails)
    def get_users_listing(request: Request):
        resp = UserListingService(request, read_db=get_read_db_session()).get_listing()
        return resp




.. _service:

Writing your very first listing API using fastapi-listing.
----------------------------------------------------------
Service layer where I write all my business logics


Creating your first **listing api** service that will be called from router to return a listing response.::

    # user_service.py

    from fastapi_listing import FastapiListing, ListingService
    from fastapi_listing.typing import FastapiRequest, SqlAlchemyQuery
    from app.dao import UserDao
    from app.schema.response.user_responses import UserListingDetails

    class UserListingService(ListingService):
        # full attribute list given in attribute section
        DEFAULT_SRT_ON = UserDao.model.id.name
        dao_kls = UserDao

        def get_listing(self):
            resp = FastapiListing(self.request, self.dao, UserListingDetails
                                    ).get_response(self.MetaInfo(self))
            return resp


* **ListingService**: class is representation of the User listing. Always extend this.
* **Attributes**: :ref:`attributes overview`
* **UserListingDetails**: Pydantic class containing required fields to add in listing, only these fields will be fetched from query. Add or remove fields from pydantic class to control query results.

Once you runserver, hit the endpoint ``localhost:8000/v1/users`` and you will receive a json response with page size 10 (default page size)

Customising your listing listing query
--------------------------------------

Extend Query Strategy
^^^^^^^^^^^^^^^^^^^^^

Getting users on basis of logged in users company.

first add your new optimised query in user dao::

    from __future__ import annotations
    from app.dao.generics import ClassicDaoFeatures
    from app.dao.model import User

    class UserDao(ClassicDaoFeatures):

        model = User

        def get_user_by_company(self, company: str):
            query = self._read_db.query(self.model).filter(self.model.company == company)
            return query


writing your own query strategy,
way 1 - writing strategy at listing service level(if its easy and you know its gonna be short why not write it just above your listing service)::

    # user_service.py

    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory


    class UserQueryStrategy(QueryStrategy):

        NAME = "user_query_v1"

        def get_query(self, *, request: FastapiRequest = None, dao: UserDao = None,
                      extra_context: dict = None) -> SqlAlchemyQuery:
            user = request.user # assuming loggen in user meta info is present
            user_comp = dao.read({"email":user.email}, fields=["company"])
            query = dao.get_user_by_company(company=user_comp.company)
            return query


    # register your query strategy with strategy factory under unique name
    strategy_factory.register_strategy(UserQueryStrategy.NAME, UserQueryStrategy)


    class UserListingService(ListingService):
        # full attribute list given in attribute section
        DEFAULT_SRT_ON = UserDao.model.id.name
        dao_kls = UserDao
        QUERY_STRATEGY = UserQueryStrategy.NAME # or "user_query_v1"

        def get_listing(self):
            resp = FastapiListing(self.request, self.dao, UserListingDetails
                                    ).get_response(self.MetaInfo(self))
            return resp


Write as many variations as you want of query strategy change anytime without breaking other logic due to human induced errors.

way 2 - writing complex query strategy preferred way is create a separate module inside **strategies** dir::

    # strategies/user_query_strategy.py

    from fastapi_listing.factory import strategy_factory
    from fastapi_listing.typing import FastapiRequest, SqlAlchemyQuery
    from fastapi_listing.strategies import QueryStrategy

    from app.dao import UserDao
    from app.dao.model import User


    NAME = "user_query_v2"


    class UserQueryStrategyV2(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: UserDao = None,
                      extra_context: dict = None) -> SqlAlchemyQuery:
            user_obj: User = dao.read({"email":request.user.email}) # getting user object

            if user_obj.access_role == "super_admin":
                query = dao.get_users_under_super_admin() # dao method to get appropriate query

            elif user_obj.access_role == "admin":
                query = dao.get_users_under_admin() # dao method to get appropriate query

            elif user_obj.access_role in ["senior_manager", "senior_director"]:
                query = dao.get_users_under_managers() # dao method to get appropriate query
            else:
                # this user should get empty results
                query = dao.get_empty_query()

            # user table have all company user data only show associated data
            query = dao.filter_by_company(company=user_obj.company)

            return query


    strategy_factory.register_strategy(NAME, DealerPreferenceQueryStrategy)

    # then simply attach this strategy to your listing service

    # user_service.py
    from app.strategies import user_query_strategy


    class UserListingService(ListingService):
        # full attribute list given in attribute section
        DEFAULT_SRT_ON = UserDao.model.id.name
        dao_kls = UserDao
        QUERY_STRATEGY = user_query_strategy.NAME # or "user_query_v2"

        def get_listing(self):
            resp = FastapiListing(self.request, self.dao, UserListingDetails
                                    ).get_response(self.MetaInfo(self))
            return resp


.. _attributes overview:

``ListingService`` attributes
-----------------------------

.. py:currentmodule:: fastapi_listing.service.listing_main


.. py:attribute:: ListingService.filter_mapper

    A ``dict`` containing allowed filters on the listing. ``{alias: value}`` where key should be an alias of field and value should be
    the field name given in model class

    for example: ``{"fnm": "User.first_name"}``

    value ``"User.first_name"`` shows relation. ``first_name`` from model ``User``. This should always be unique. You could go sane defining your values
    like this which will help you when debugging. split on ``.`` happens and last value is assumed to be actual field.

:ref:`alias overview`?

.. py:attribute:: ListingService.sort_mapper

    A ``dict`` containing allowed sorting field on the listing

:ref:`alias overview`?

.. py:attribute:: ListingService.DEFAULT_SRT_ORD

    defining listing data default sorting order: **asc**, **dsc**

.. py:attribute:: ListingService.PAGINATE_STRATEGY

    defining listing service pagination strategy unique name. Default ``default_paginator``

.. py:attribute::  ListingService.QUERY_STRATEGY

    defining listing service query strategy unique name. Default ``default_query``

.. py:attribute:: ListingService.SORTING_STRATEGY

    defining listing service sorting strategy unique name. Default ``default_sorter``

.. py:attribute:: ListingService.SORT_MECHA

    defining listing service sort process executor. Default ``singleton_sorter_mechanics``

.. py:attribute:: ListingService.FILTER_MECHA

    defining listing service filter process executor. Default ``iterative_filter_mechanics``

.. py:attribute:: ListingService.dao_kls

    defining listing service :ref:`dao` class. should be created extending ``GenericDao``





.. _alias overview:

Why use alias
-------------

* Avoid giving away original column names at client level. A steps towards securing and maintaining abstraction at api level.
* Shorter alias names are light weight. payload looks more friendly.
* Saves a little bit of bandwidth by saving communicating some extra characters.
* save coding time with shorter keys.






