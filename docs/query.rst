Customising your listing  query
-------------------------------

By default FastAPI Listing prepares simple queries which may look like:

``select a,b,c,d from table``

where ``a,b,c,d`` are columns that you provide either via pydantic serializer or as a list of strings.

Remember this?

``FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListindDetail).get_response(self.MetaInfo(self))``

``FastapiListing(self.request, self.dao, fields_to_fetch=['a', 'b', 'c', 'd']).get_response(self.MetaInfo(self))``

core ``class`` invokes ``get_default_read`` to prepare above mentioned vanilla query. You can easily overwrite this method
in your dao class to write your custom query.

You can either pass ``pydantic_serializer``/``fields_to_fetch`` or not as you will be writing custom ``query``.


Advanced guide for generating listing query
-------------------------------------------

Most of the time you will be writing your own custom optimised queries for retrieving listing data and it isn't unusual to write
multiple queries that gets fired on different context.

A brief example could be:

You have a system where users are grouped together in different roles. Each group of user are separated on
different layer of data levels so you need to check two thing in every listing API call

1. What role logged in user have,

2. On which data layer the user lies and show only relevant or allowed data,

To tackle this situation you may wanna write different query for each group of users.
Some queries may look simple some may look advanced some may even corporate caching layer.
This part could easily kill your listing API performance if not handled well or a small change could induce huge errors.

Going back to the topic.

As mentioned in the basics section you can create :ref:`strategies<querybasics>` encapsulating query generation logics and abstracting query preparation from rest of the code.

First Example
^^^^^^^^^^^^^

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
                      extra_context: dict = None) -> QueryContext:
            # as request and dao args are self explanatory
            # extra_context is a chained variable that can carry contextual data from one place
            # to another place. extremely helpful when passing args from router or client.
            dept_no: str = dept_no # assuming we found dept no of logged in user
            return dao.get_employees_by_dept(dept_no) # method defined in dao class

    # it is important to register your strategy with factory for use.
    strategy_factory.register("<whatever name you choose>", DepartmentWiseEmployeesQuery)

.. _dept_emp_q_stg:

Add your new listing query to employee dao

.. code-block:: python


    from fastapi_listing.context.sqlalchemy import SqlAlchemyQueryContext

    class EmployeeDao(ClassicDao):
        name = "employee"
        model = Employee

        def get_employees_by_dept(self, dept_no: str) -> SqlAlchemyQueryContext:
            # assuming we have one to one mapping and we are passing manager department here
            query = self._read_db.query(self.model
                                        ).join(DeptEmp, Employee.emp_no == DeptEmp.emp_no
                                        ).filter(DeptEmp.dept_no == dept_no)
            return SqlAlchemyQueryContext(query)


.. code-block:: python
    :emphasize-lines: 9

    @loader.register()
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        query_strategy = "default_query" # strategy chosen in case runtime switch condition not satisfied
        def get_listing(self):
            if user == manager: # imaginary conditions
                self.switch("query_strategy","<whatever name we choose>") # switch strategy on the fly on object/request level

            resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
            return resp

In above example I have decided to make a switch for query strategy at runtime. So whenever a department manager logs in ``query_strategy`` will be
switched to fetch relative data and whenever other user logs in they will see global data because you have a default ``query_strategy`` placed as well. Lets call it context based switching.

Second Example
^^^^^^^^^^^^^^

1. **Different Ways to Handle Queries:**

   If you want to deal with context based switching separately, you can encapsulate logic in a single strategy class. Add instructions to generate context based queries. Inject this class into your listing service ``default_strategy = <your new strategy class>``.

.. code-block:: python

    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory
    from sqlalchemy.orm import Query


    class EmployeesQuery(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                      extra_context: dict = None) -> Query:
            # assuming in this scope we know about logged in user
            user = logged_in_user
            match user.role:
                case "manager" :
                    query = self.get_manager_query(user)
                    ... # you define other contexts like manager
                    ...
                    ...
                case _" : #encountering any unknown context return empty query
                    query = dao.get_empty_query() # defined in classic dao

            return query

        def get_manager_query(self, user, dao) -> Query:
            # assuming we have a way to get dept_no
            dept_no = dao.get_dept_no_via_user(user)
            return dao.get_employees_by_dept(dept_no)

    # it is important to register your strategy with factory for use.
    strategy_factory.register("<whatever name you choose for employee query class>", EmployeesQuery)

.. code-block:: python

    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        query_strategy = "<whatever name you choose for employee query class>"
        def get_listing(self):
            # if user == manager: # imaginary conditions
            #     self.switch("query_strategy","<whatever name we choose>") # switch strategy on the fly on object/request level

            # we made our query strategy class to exhibit different behaviour no need of above code
            resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
            return resp

2. **Two Approaches for Query Handling:**

   Some people might want to decide which query method to use right where the service is like we did in first example. They like to keep the way queries work separate and simple. They can use ``switch`` to easily switch between different methods.

3. **Choosing the Right Approach:**

   It's completely a users choice to make their objects behave in a certain way. FastAPI Listing is capable of adhering to users need 😍 whether you wanna keep your context based switching at service level
   or at strategy level (query strategy class) inject it in your listing service as mention in first point and make your query strategy ``object`` capable of behaving context wise.

Personally I mixes both of these when I know strategies are going to be simple I tend to make strategy objects capable of handlind different contexts but
when I know or see my single strategy class is becoming hard to maintain I tend to breakdown them to handle specefic context at a time as a result having
single responsibility objects.

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