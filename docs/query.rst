Customising your listing query
-------------------------------

By default, FastAPI Listing prepares a simple query, roughly:

``select a, b, c, d from table``

where ``a, b, c, d`` are the columns you provide, either via a Pydantic serializer or as a list of
strings.

Recall from the tutorial:

``FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListindDetail).get_response(self.MetaInfo(self))``

``FastapiListing(self.request, self.dao, fields_to_fetch=['a', 'b', 'c', 'd']).get_response(self.MetaInfo(self))``

Internally, this calls ``get_default_read`` on your DAO to build that query. Override it on your own DAO
class to write a custom query instead - ``pydantic_serializer``/``fields_to_fetch`` become optional once
you're building the query yourself.


Advanced guide for generating listing queries
-----------------------------------------------

Most non-trivial listing APIs need more than one query, chosen based on context - and getting this wrong
tends to be where listing API performance actually breaks down.

A representative example: users belong to different roles, and each role should only see a subset of
the data. Every listing request needs to answer two questions:

1. what role does the logged-in user have?
2. which data layer does that role's data live in?

Different roles may need meaningfully different queries - some simple, some more involved, some backed
by a cache. As covered in the basics, :ref:`query strategies <querybasics>` are how you encapsulate this,
keeping query construction separate from the rest of the service.

First example: context-based switching at the service level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Say you have a department-manager table:

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

A department manager should only see employees in their own department (an engineering manager sees
engineering staff, and nothing else). Here's a query strategy for that:

.. code-block:: python

    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory


    class DepartmentWiseEmployeesQuery(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                      extra_context: dict = None) -> QueryContext:
            # extra_context threads contextual data from one stage of the pipeline to
            # another - handy for passing values in from the router or the client
            dept_no: str = dept_no  # assume we've already resolved the logged-in user's dept_no
            return dao.get_employees_by_dept(dept_no)  # defined on the DAO below

    # strategies must be registered with the factory before use
    strategy_factory.register_strategy("<a name you choose>", DepartmentWiseEmployeesQuery)

.. _dept_emp_q_stg:

Add the corresponding method to the employee DAO:

.. code-block:: python

    from fastapi_listing.context.sqlalchemy import SqlAlchemyQueryContext

    class EmployeeDao(ClassicDao):
        name = "employee"
        model = Employee

        def get_employees_by_dept(self, dept_no: str) -> SqlAlchemyQueryContext:
            # assumes a one-to-one mapping; dept_no here is the manager's own department
            query = self._read_db.query(self.model
                                        ).join(DeptEmp, Employee.emp_no == DeptEmp.emp_no
                                        ).filter(DeptEmp.dept_no == dept_no)
            return SqlAlchemyQueryContext(query)

Then switch to it at the service level, based on context:

.. code-block:: python
    :emphasize-lines: 9

    @loader.register()
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        query_strategy = "default_query"  # used unless the switch below fires
        def get_listing(self):
            if user == manager:  # illustrative condition
                self.switch("query_strategy", "<a name you choose>")  # switch strategy for this request

            resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
            return resp

Here, the switch happens at the service level: a department manager gets the department-scoped query,
every other user gets the default. Call this context-based switching.

Second example: encapsulating the switch inside the strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you'd rather keep context-based branching out of the service entirely, put it inside a single
strategy class instead, and inject that strategy as ``query_strategy``:

.. code-block:: python

    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory
    from fastapi_listing.context import QueryContext


    class EmployeesQuery(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                      extra_context: dict = None) -> QueryContext:
            user = logged_in_user  # assume this scope has access to the logged-in user
            match user.role:
                case "manager":
                    query = self.get_manager_query(user, dao)
                    # ... other roles handled the same way
                case _:
                    query = dao.get_empty_query()  # any unrecognised role gets nothing back

            return query

        def get_manager_query(self, user, dao) -> QueryContext:
            dept_no = dao.get_dept_no_via_user(user)
            return dao.get_employees_by_dept(dept_no)

    # strategies must be registered with the factory before use
    strategy_factory.register_strategy("<a name for this strategy>", EmployeesQuery)

.. code-block:: python

    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        query_strategy = "<a name for this strategy>"
        def get_listing(self):
            # the strategy itself now handles context - no switch call needed here
            resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
            return resp

Which approach to use
^^^^^^^^^^^^^^^^^^^^^^

Both are valid; it comes down to where you'd rather keep the branching logic:

* keep it at the service level (first example) if you like seeing the switch happen right where the service is defined
* keep it inside the strategy (second example) if you'd rather the service stay simple and let the strategy object handle context on its own

In practice, a mix often works best: when a strategy is simple, let it handle its own context; once a
single strategy class becomes hard to follow, split it into one class per context so each stays focused
on a single responsibility.

Backend-agnostic query objects (SQLAlchemy is no longer the only option)
--------------------------------------------------------------------------

Every place that used to pass around a raw SQLAlchemy ``Query`` now passes around a ``QueryContext``
(``fastapi_listing.context.QueryContext``) instead. For the default SQLAlchemy backend this is just a thin
wrapper - ``SqlAlchemyQueryContext`` - around your existing ``Query``, so ``get_query``/custom ``QueryStrategy``
methods should return one of these instead of a bare ``Query``:

.. code-block:: python

    from fastapi_listing.context.sqlalchemy import SqlAlchemyQueryContext

    class MyQueryStrategy(QueryStrategy):

        def get_query(self, *, request=None, dao=None, extra_context: dict = None) -> QueryContext:
            query = dao.get_default_read([...])  # a GenericDao already returns a QueryContext
            return query

If you need to do something the canonical filter/sort vocabulary doesn't cover (joins, eager loading,
aggregates, ...), drop down to the raw SQLAlchemy ``Query`` via ``context.native``, mutate it however you like,
then hand it back via ``context.with_native(new_query)``.

This same ``QueryContext`` contract is what lets FastAPI Listing support non-ORM backends - a
``ClickHouseQueryContext`` (``fastapi_listing.context.clickhouse``) ships as a reference implementation,
paired with ``fastapi_listing.dao.ClickHouseDao``, proving the same ``Filter``/``SortingOrderStrategy``/
``PaginationStrategy`` classes work unmodified against raw parameterized SQL, not just an ORM. See
:ref:`learnfilters` for how filters stay backend-agnostic through the shared ``Op`` vocabulary.

Escape hatches: when the canonical vocabulary genuinely isn't enough
---------------------------------------------------------------------

Canonical filters/sort/pagination cover comparisons on a plain column, single-column sort, and
offset/limit pagination - the common case. Real queries aren't always that simple. ``ClickHouseQueryContext``
has an escape hatch for each level of "not simple enough":

``from_raw_sql`` - the full bypass
    .. code-block:: python

        raw_sql = build_my_complicated_query(account_id=..., date_range=...)  # CTEs, joins,
                                                                                # window functions,
                                                                                # a table function -
                                                                                # however you already
                                                                                # build it
        context = ClickHouseQueryContext.from_raw_sql(client=my_client, sql=raw_sql, params={...})

    Wraps your query as a derived table. Canonical filters/sort/pagination can still layer ``WHERE``/
    ``ORDER BY``/``LIMIT`` on top of whatever columns your query exposes - or you can leave ``filter_mapper``
    empty and let the raw SQL stand entirely as-is. Structural, request-scoped query shape (which account,
    which date range, how a metric is computed) belongs here, built once by your ``QueryStrategy``/DAO -
    not something a generic ``Filter`` class should know about.

``HavingMixin`` - filtering on an aggregated field
    .. code-block:: python

        from fastapi_listing.filters.generic_filters import HavingMixin, DataGreaterThanFilter

        class TotalConversionsAbove(HavingMixin, DataGreaterThanFilter):
            pass

    Same canonical ``Op`` (``GT``, in this case), routed to ``HAVING`` instead of ``WHERE`` - for filtering
    on the result of a ``GROUP BY`` (``SUM(x) > 100``), which ``WHERE`` cannot express. Available on
    ``SqlAlchemyQueryContext`` too (``context.having(field=..., op=..., value=...)``, mirroring ``.having()``
    on a SQLAlchemy ``Query``).

``order_by_raw`` - a compound ordering rule
    .. code-block:: python

        context.order_by_raw(f"(site_id = {int(own_domain_id)}) DESC, `{sort_column}` {direction}")

    For an ordering rule that isn't a single ``field, direction`` pair - a tiebreak column pinned first,
    then the user's chosen sort, or any other multi-key expression the canonical ``order_by()`` can't
    represent.

``add_raw_condition`` - a backend-specific SQL function, per filter
    .. code-block:: python

        from fastapi_listing.context.clickhouse import quote_identifier

        class MultiSearchAnyFilter(CanonicalFilter):
            def filter(self, *, field=None, value=None, context=None):
                col = quote_identifier(self.extract_field(field))
                return context.add_raw_condition(
                    f"multiSearchAnyCaseInsensitive({col}, {{needles}})", needles=value.get("list") or [])

    For a single filter that needs a builtin ClickHouse function (a full-text search primitive, an array
    operator, ...) with no canonical ``Op`` equivalent. Values still flow through the driver's real
    parameter binding (``%(name)s``) - never string-formatted into the SQL text - only the resolved
    field/column identifier is spliced in directly (via ``quote_identifier``), the same way every other
    op in ``ClickHouseQueryContext`` already handles identifiers vs. values.

The rule of thumb across all four: reach for the narrowest escape hatch that solves your problem.
Need a different clause or expression for one filter/one sort? Use ``having``/``order_by_raw``/
``add_raw_condition``. Need a fundamentally different query shape (CTEs, joins, a table function)?
``from_raw_sql`` is the one that hands you full control.
