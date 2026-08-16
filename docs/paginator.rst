Customising Paginator Strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default pagination strategy slices data into variable-sized pages and covers most cases. For a huge
table, or a use case the default doesn't fit, extend the base paginating strategy to write your own -
for example, a keyset/range-based strategy, or a "previous"/"next" style paginator that avoids a count
query entirely.

.. code-block:: python
    :emphasize-lines: 3, 4

    @loader.register()
    class EmployeeListingService(ListingService):
        paginate_strategy: str = "default_paginator"
        default_page_size: int = 10  # change to alter the default page size


Post-fetch business logic
--------------------------

Not everything belongs in the query. Filling in zero-value rows for missing time buckets, a tie-break
re-sort that can't be expressed in SQL, reshaping rows differently for CSV export than for the JSON
response - these are all real needs that have nothing to do with filtering/sorting/pagination, but if
your listing framework has no dedicated seam for them they tend to get bolted onto whatever's nearby
(usually the endpoint function itself), which is exactly how disciplined query-building code turns into
an unmaintainable pile over time.

``PaginationStrategy`` has one governed home for this: override ``postprocess``.

.. code-block:: python

    class MyPaginationStrategy(PaginationStrategy):

        def postprocess(self, rows, extra_context: dict):
            # rows is whatever context.fetch() returned - runs after fetch, before the Page envelope is built
            return rows

It's identity by default and runs once, right after the rows are fetched and before ``hasNext``/``totalCount``/etc.
are assembled into the response. Do post-fetch business logic here, not by overriding ``_get_page``/
``_get_page_without_count`` (those exist to change the *page envelope shape*) or by reaching into the DAO.

.. _alias overview:

Why use an alias
-----------------

* Avoids exposing real column names to the client - a small step toward keeping the API's abstraction boundary intact.
* Shorter aliases keep response payloads lighter.
* Saves a little bandwidth by not sending longer key names.
* Saves coding time with shorter keys.
