

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

Sorting on a computed or aggregated field (e.g. a CTE)
-------------------------------------------------------

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

How FastAPI Listing reads sorter params:

``[{"field":"alias", "type":"asc"}]`` or ``[{"field":"alias", "type":"dsc"}]`` 📝

**If you have an existing running service that means you already have running remote client setup that will be sending different named query params for filter, then
use the** :ref:`adapter <adapter_attr>` **to make your existing listing service adapt to your existing code.**