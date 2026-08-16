The Basics
==========

Installation
------------

To install FastAPI Listing, run:

.. code-block:: bash

    pip install fastapi-listing

For the ClickHouse reference backend, install the extra as well:

.. code-block:: bash

    pip install fastapi-listing[clickhouse]

.. _dao overview:


The DAO (Data Access Object) layer
-----------------------------------

FastAPI Listing uses a `DAO <https://www.oracle.com/java/technologies/data-access-object.html#:~:text=The%20Data%20Access%20Object%20(or,to%20a%20generic%20client%20interface>`_
layer as the one place responsible for talking to the database.

Benefits:

* A dedicated place for writing queries
* Clear separation between data access and business logic
* Queries can change independently of the rest of the service
* Shared query logic has one obvious home instead of being copied across endpoints
* Cleaner imports at the call site

FastAPI Listing uses a single-table DAO: each DAO class is bound to one model.

Dao objects
^^^^^^^^^^^

.. py:class:: GenericDao

When creating a DAO class, extend ``GenericDao``, which comes with the necessary setup code. Every DAO
object exposes two session attributes, scoped to the DAO layer only:

``_read_db`` and ``_write_db``

Use these to communicate with the database. Keeping them separate is preparation for a read
replica/primary split, should you need one later - if you don't have one, point both at the same
session; there's no cost to doing so.

``GenericDao`` is the SQLAlchemy-backed default. For a non-ORM backend, extend ``DaoAbstract``
directly instead - see :doc:`query` for how the reference ``ClickHouseDao`` does this.

Dao class attributes
^^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: GenericDao.model

    The SQLAlchemy model class. **Required.**

.. py:attribute:: GenericDao.name

    A user-defined, unique name for the DAO class. **Required.**


The Strategy layer
-------------------

Encapsulates:

* fetching data (Query Strategy)
* applying sorting, if any, after fetching data (Sorting Strategy)
* paginating the fetched data (Paginating Strategy)

The strategy pattern fits well here because these concerns tend to vary independently: which query to
run can depend on the logged-in user's role, which data layer they're allowed to see, performance
constraints, or a legacy schema you can't change. You'll often end up with multiple ways to build a
query, sort, or paginate - the strategy pattern gives each variant its own object rather than a growing
pile of conditionals in one place.

Query Strategy
^^^^^^^^^^^^^^

Decides what listing query to run, in context. The default ``default_query`` strategy generates a
``select a, b, c, d from some_table`` query using SQLAlchemy, where ``a, b, c, d`` are the columns you
provide.

.. _querybasics:

That covers most simple cases.

.. py:class:: QueryStrategy

Create your own query strategy by extending the base class.

A concrete example of where the strategy pattern helps: you have an employee table and an
organisational hierarchy - Director, Assistant Director, Division Manager, Manager, Lead, then
individual contributors. You need an API that only shows employees under the logged-in user.

There are two reasonable ways to structure that with strategies.

**One strategy class per context:**

``class DirectorQueryForEmp(QueryStrategy)``

``class AssistantDirectorQueryForEmp(QueryStrategy)``

``class DivisionManagerQueryForEmp(QueryStrategy)``

``class ManagersQueryForEmp(QueryStrategy)``

``class LeadsQueryForEmp(QueryStrategy)``

Encapsulate the logic for deciding which one applies, and choose at runtime.

**Or one strategy class handling every context:**

``class EmployeeQuery(QueryStrategy)``

Branch on context inside a single class. Which style fits is a judgment call based on how the branches
are likely to grow.

Benefits of separating by context:

* the intent of each class is clear at a glance
* each is a small, focused unit
* easy to extend with a new role or a superuser case without touching the others

Sorting Strategy
^^^^^^^^^^^^^^^^

Applies a sort order to your query. Nothing more than that.

.. py:class:: SortingOrderStrategy

``SortingOrderStrategy`` understands two client-facing keywords, ``asc`` and ``dsc``, and sorts
accordingly.

Using different keywords on the client side? See :ref:`the adapter layer <adapterbenefit>`.


Paginator Strategy
^^^^^^^^^^^^^^^^^^^

Paginates query results and returns a paginated response to the client.

.. py:class:: PaginationStrategy

* Configure pagination parameters directly.
* Supports dynamic page sizing.
* Set ``default_page_size`` for requests that don't specify a page size.
* Set ``max_page_size`` to cap how large a page a client can request.
* Write your own paginator for lazy loading, range-based slicing, or other strategies.

Have an existing set of pagination parameters? See :ref:`the adapter layer <adapterbenefit>`.

The Filters layer
^^^^^^^^^^^^^^^^^^

Usually the most-used part of a listing service, and one where things get messy fast without a bit of
discipline.

Filtering is abstracted so you never write a chain of ``if``/``else`` branches in a listing endpoint,
even with a dozen filters applied.

Inspired by Django admin's approach to filters: define a filter once, import it anywhere, and reuse it
across listing services. ``generic_filters`` ships a set of these ready to use.

Need this to work with an existing client's filter parameters? See :ref:`the adapter layer <adapterbenefit>`.

.. _intereptorbasics:

The Interceptor layer
^^^^^^^^^^^^^^^^^^^^^^

Lets you write a custom execution plan for filters or sorters.

* The default filter execution plan applies filters one at a time, iteratively.
* The default sort execution plan sorts on one field at a time.

Why this exists: applying several filters independently, one after another, doesn't always give the
same result as applying them together. You may also want to combine two filters into a single, more
efficient query rather than running them in sequence.

Similarly for sorting - multi-field sort is supported, but on large tables it tends to hurt performance
more than it helps. Filtering the data down first, then sorting, is usually the better trade-off.

An interceptor is where you take control of *how* filters and sorters get applied, beyond the default
one-at-a-time behavior.

.. _adapterbenefit:

Params Adapter layer
^^^^^^^^^^^^^^^^^^^^^

Every client encodes filter/sort/pagination parameters a little differently. See, for example, this
`Stack Overflow discussion <https://drive.google.com/uc?export=view&id=1X1DiX7zRhnmJfw-t71Vgk4jnKVIExJzP>`_
of how differently teams approach it.

Whatever convention your client already uses, ``CoreListingParamsAdapter`` lets FastAPI Listing adapt to
it: read the raw HTTP request, and translate its query parameters into the shape FastAPI Listing expects
natively.

FastAPI Listing looks for three keys - ``sort``, ``filter``, and ``pagination`` - and the adapter is
responsible for returning them translated into the native shape:

- **Filter**: ``[{"field": "<your_field>", "value": {"search": "<your_value>"}}]`` - a list of filters, any number of which may be applied together.
- **Sort**: ``[{"field": "<your_field>", "type": "<asc or dsc>"}]`` - a list of sort instructions (single-field sort by default; customisable).
- **Pagination**: ``{"pageSize": "<integer page size>", "page": "<integer page number>"}`` - supports dynamic page sizing.

This is particularly useful if you're adding FastAPI Listing to an existing service: you can adopt it
without changing anything on the client side.

Filters also support range- and list-based semantics beyond a single value - see :doc:`filters`.


Conclusion
----------

That covers the theory. With a basic understanding of each component, you're ready for the tutorial,
which walks through building a listing API end to end.
