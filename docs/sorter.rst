

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

How FastAPI Listing reads sorter params:

``[{"field":"alias", "type":"asc"}]`` or ``[{"field":"alias", "type":"dsc"}]`` 📝

**If you have an existing running service that means you already have running remote client setup that will be sending different named query params for filter, then
use the** :ref:`adapter <adapter_attr>` **to make your existing listing service adapt to your existing code.**