

Customising Paginator Strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have a default pagination class. Which handles slicing of our data into pages with variable size. The provided pagination ``class``
is simple and gets the work done. If you wanna write your own efficient paginating strategy for huge tables or any other use case
you could write one by extending existing base or abstract paginating strategy ``class``.

For example you may wanna implement a paginating strategy which works on range ids for huge tables or only `previous` `next` pagination strategy and avoid
any count query.


.. code-block:: python
    :emphasize-lines: 3, 4

    @loader.register()
    class EmployeeListingService(ListingService):
        paginate_strategy: str = "default_paginator"
        default_page_size: int = 10 # default page size modify this to change default page size.



Post-fetch business logic
-------------------------

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

Why use alias
-------------

* Avoid giving away original column names at client level. A steps towards securing and maintaining abstraction at api level.
* Shorter alias names are light weight. payload looks more friendly.
* Saves a little bit of bandwidth by saving communicating some extra characters.
* save coding time with shorter keys.