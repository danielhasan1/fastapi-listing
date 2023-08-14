

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



.. _alias overview:

Why use alias
-------------

* Avoid giving away original column names at client level. A steps towards securing and maintaining abstraction at api level.
* Shorter alias names are light weight. payload looks more friendly.
* Saves a little bit of bandwidth by saving communicating some extra characters.
* save coding time with shorter keys.