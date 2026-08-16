Adding Sorters to your listing API
----------------------------------

Sorting is left to the database, so this is simple - FastAPI Listing provides a strategy class that
applies a sort order to your listing query.

.. code-block:: python
    :emphasize-lines: 3, 4, 5

    @loader.register()
    class EmployeeListingService(ListingService):
        default_srt_ord: str = "dsc"  # "asc" for ascending; "dsc" is the default (latest data first)
        default_srt_on = "Employee.emp_no"  # field used when the request specifies no sort parameter
        sort_mapper = {
            "empid": "emp_no",
        }

``sort_mapper`` works like ``filter_mapper``: ``empid`` is what the remote client sends, ``emp_no`` is
the field actually used to sort. It's the set of sort fields a client is allowed to request.

Sorting on the primary model looks like the example above.

To sort on a joined table's field, add a resolver just like you would for a filter:

.. code-block:: python
    :emphasize-lines: 2

    sort_mapper = {
        "deptno": ("dept_no", lambda x: getattr(DeptEmp, x))
    }

Unlike filters, there's no central sorter factory requiring unique names - since sorting is delegated
entirely to the database, there's no registration step to worry about. Using the ``model.field``
convention is still recommended for consistency with ``filter_mapper``.

Just like the filter interceptor, a sorter interceptor lets you override the default one-field-at-a-time
sort behavior and apply your own multi-field sorting logic.

Sorting on a computed or aggregated field (e.g. a CTE)
--------------------------------------------------------

``sort_mapper``'s callable form (above) resolves a field once, at class-definition time - that works for
a joined table's column, but not for a column that only exists on a query built per-request, such as a
CTE aggregating a metric. For that, write a custom sorting strategy that reads the column back from
``extra_context`` instead of the static model - stash it there from your ``QueryStrategy`` when you build
the CTE, since both ``get_query()`` and ``sort()`` receive the same ``extra_context`` dict for a given
request:

.. code-block:: python

    from fastapi_listing.abstracts import AbsQueryStrategy, AbsSortingStrategy
    from fastapi_listing.context import QueryContext
    from fastapi_listing.factory import strategy_factory

    class EmployeeMetricsQueryStrategy(AbsQueryStrategy):
        def get_query(self, *, request=None, dao=None, extra_context=None) -> QueryContext:
            context = dao.get_default_read(...)  # builds/joins your CTE
            extra_context["metrics_cte"] = ...    # keep a handle to the CTE for the sort stage
            return context

    class ComputedFieldSortingStrategy(AbsSortingStrategy):
        def sort(self, *, context: QueryContext = None, value=None, extra_context=None) -> QueryContext:
            cte = extra_context["metrics_cte"]
            column = getattr(cte.c, value["field"])
            return context.order_by(field=column, direction=value["type"])

    strategy_factory.register_strategy("employee_metrics_query", EmployeeMetricsQueryStrategy)
    strategy_factory.register_strategy("computed_field_sorter", ComputedFieldSortingStrategy)

    @loader.register()
    class EmployeeListingService(ListingService):
        query_strategy = "employee_metrics_query"
        sorting_strategy = "computed_field_sorter"
        sort_mapper = {
            "indexedpages": "total_indexed_pages",
        }

``context.order_by()`` works with any SQLAlchemy column-like object - a CTE's labeled column included,
not just a mapped model attribute - so no library change is needed to sort on one; only a sorting
strategy that knows where to find it.

How FastAPI Listing reads sort parameters:

``[{"field": "alias", "type": "asc"}]`` or ``[{"field": "alias", "type": "dsc"}]``

Adapting an existing client's sort parameter names? See :ref:`the adapter layer <adapter_attr>`.
