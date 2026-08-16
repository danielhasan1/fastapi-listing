.. _learnfilters:

Adding Filters to your listing API
----------------------------------

Filtering is the most-used part of a listing API, and also the part most likely to turn messy without
some discipline.

Start with a simple request: filter the employee listing by ``gender``.

.. code-block:: python
    :emphasize-lines: 1, 7

    from fastapi_listing.filters import generic_filters


    @loader.register()
    class EmployeeListingService(ListingService):

        filter_mapper = {
            "gdr": ("Employee.gender", generic_filters.EqualityFilter),
        }

        # rest of the definition is unchanged

``generic_filters`` holds the commonly used filters that ship with FastAPI Listing - reusable, and each
supports referencing a secondary model's field in place. There's a filter here for most common cases:


.. list-table::
   :widths: auto

   * - ``EqualityFilter``
     - equality filter, ``a == b``
   * - ``InEqualityFilter``
     - inequality filter, ``a != b``
   * - ``InDataFilter``
     - ``in`` filter, ``a in (b)``
   * - ``BetweenUnixMilliSecDateFilter``
     - range filter, ``between(start, end)``, over Unix timestamps - avoids ambiguity between date formats
   * - ``StringStartsWithFilter``
     - like filter, ``a like b%``
   * - ``StringEndsWithFilter``
     - like filter, ``a like %b``
   * - ``StringContainsFilter``
     - substring filter, ``a like %b%`` - recommended only on small tables
   * - ``StringLikeFilter``
     - string equality filter, ``a like b``
   * - ``DataGreaterThanFilter``
     - greater-than filter, ``a > b``
   * - ``DataGreaterThanEqualToFilter``
     - greater-than-or-equal filter, ``a >= b``
   * - ``DataLessThanFilter``
     - less-than filter, ``a < b``
   * - ``DataLessThanEqualToFilter``
     - less-than-or-equal filter, ``a <= b``
   * - ``DataGropByElementFilter``
     - aggregation filter, ``a group by b``
   * - ``DataDistinctByElementFilter``
     - distinct filter, ``distinct a``
   * - ``HasFieldValue``
     - null-check filter, ``a is null`` or ``a is not null``
   * - ``MySqlNativeDateFormateRangeFilter``
     - range filter, ``between(a, b)``, over MySQL's native date format


Recall :ref:`filter_mapper <filter_mapper_label>` from the tutorial - each entry has three parts:

1. the key sent by the remote client
2. the tuple:

   * first item: ``model.field`` - the field on the primary table the filter applies to
   * second item: the filter class

That's a complete, working filter.

Aliasing your fields (the dict key) over their real names has a few concrete benefits:

1. the actual column name is never exposed to the client
2. request URLs stay short and meaningful to other developers, not database internals
3. less information leaks through the URL than would otherwise

How FastAPI Listing reads filter parameters:

* single-value filter - ``[{"field": "<filter_mapper key>", "value": {"search": "<value>"}}]``
* multi-value filter - ``[{"field": "<filter_mapper key>", "value": {"list": [<values>]}}]``
* range filter - ``[{"field": "<filter_mapper key>", "value": {"start": "<value>", "end": "<value>"}}]``

Adapting an existing client's filter parameter names? See :ref:`the adapter layer <adapter_attr>`.


Customising your filters
^^^^^^^^^^^^^^^^^^^^^^^^

Say you want to filter on a field from the ``DeptEmp`` model rather than the listing's primary model. A
filter written like this:

.. code-block:: python

    filter_mapper = {
        "gdr": ("Employee.dept_no", generic_filters.EqualityFilter),
    }

raises an ``AttributeError``, as expected - the primary model has no such field, and only a primary
model may be attached to a listing service directly.

To filter on a secondary model's field, add a resolver as a third tuple item:

.. code-block:: python
    :emphasize-lines: 2

    filter_mapper = {
        "dpt": ("Employee.DeptEmp.dept_no", generic_filters.EqualityFilter, lambda x: getattr(DeptEmp, x))
    }

The lambda tells the filter which model's field to use when applying it.

Why the chained name, ``Employee.DeptEmp.dept_no``? Filters register centrally in a factory keyed by
field path, which must be unique - two filters can't register under the same path. The alias
(``filter_mapper`` key) can repeat across listing services, and different schemas can share column
names, but a chained name like ``Employee.DeptEmp.dept_no`` makes the relationship explicit (``Employee``
to ``DeptEmp``, field ``dept_no``) while staying unique. You're free to use a different naming
convention, as long as it stays unique and legible.

Note that a filter like this only works if the listing's query strategy already joins in ``DeptEmp`` -
see :ref:`the dept-emp query strategy <dept_emp_q_stg>`.

Writing a custom filter
^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes the built-in filters don't cover a use case - here, a filter that scans across both
``first_name`` and ``last_name`` for a full-name match:

.. code-block:: python
    :emphasize-lines: 2, 4, 6

    from fastapi_listing.filters import generic_filters
    from fastapi_listing.dao import dao_factory
    from fastapi_listing.context import QueryContext

    class FullNameFilter(generic_filters.CanonicalFilter):

        def filter(self, *, field: str = None, value: dict = None, context: QueryContext = None) -> QueryContext:
            # field isn't needed here - this filter has full control over its own implementation
            if value:
                emp_dao: EmployeeDao = dao_factory.create("employee", replica=True)
                emp_ids: list[int] = emp_dao.get_emp_ids_contain_full_name(value.get("search"))
                native = context.native.filter(self.dao.model.emp_no.in_(emp_ids))
                context = context.with_native(native)
            return context

This inherits from ``CanonicalFilter`` (``generic_filters``); ``CommonFilterImpl`` remains as a
deprecated alias for one release if you're upgrading existing code. A custom filter implements a single
``filter`` method with a fixed signature - note the last argument is ``context``, a backend-agnostic
``QueryContext``, rather than a raw SQLAlchemy ``query``. For SQLAlchemy-specific behavior like a fluent
``.filter()`` chain, reach the underlying ``Query`` via ``context.native``, mutate it, and hand it back
via ``context.with_native(...)``. The filter's value arrives as a ``dict``.

This example also uses the DAO factory, which lets any registered DAO be used from anywhere, not just
its own listing service. Filter, then return the (possibly rewrapped) context - the filter interceptor
calls this implicitly; there's nothing else to wire up.

Most built-in filters need none of this: they declare a canonical ``op`` (see ``fastapi_listing.ops.Op``)
and hand off to the context - ``EqualityFilter``, ``InDataFilter``, and the rest of ``generic_filters``
work unmodified whether the DAO is backed by SQLAlchemy or a non-ORM backend like the reference
``ClickHouseDao``. Reach for ``context.native`` only when the canonical ``Op`` vocabulary genuinely can't
express what you need.

Why an interceptor, and when to write one
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An example of where a custom interceptor earns its keep:

Say you have a product listing with a mapping table linking products to groups, and groups to a parent
group:

.. code-block:: sql

    id | product_id | group_id | sub_group_id

You've added filters for group, sub-group, and product, each resolving IDs from the mapping table before
applying an ``in`` filter. So when a client applies:

* a group filter - your group filter runs
* a group and sub-group filter together - both run, the sub-group filter still seeing the group filter, since the client hasn't removed it
* group, sub-group, and product together - all three run

The default interceptor applies filters one at a time, iteratively, which can give the wrong result here.
Consider filtering by group ``A`` and sub-group ``A_a`` together:

``select product_id from mapping where group_id = 'A';``

feeds those product IDs into an ``in`` filter. Applying the sub-group filter next repeats the process
independently:

``select product_id from mapping where sub_group_id = 'A_a';``

Each filter resolves its own product IDs and applies them separately, rather than the two constraints
being applied together - the two ``in`` filters don't compose into "products in group A AND sub-group
A_a." What's actually needed is:

``select product_id from mapping where group_id = 'A' and sub_group_id = 'A_a';``

A custom interceptor can detect that both filters are applied together and combine them into a single
query like this one, rather than resolving each independently. This is exactly the kind of case where an
interceptor earns its complexity: reducing several dependent filters into one correct, efficient query.
