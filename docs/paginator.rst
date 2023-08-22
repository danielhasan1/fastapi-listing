

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

In pydantic there is an option of ``alias``. You can actually hide your field names under aliases or replace your actual field names with provided aliases.
That's a wonderful feature and I use it all the time:
* to abstract away the actual column names
* if a field name is too big I choose a light ``alias``
* helps in lowering network bandwidth
* language localization
* you can use names that are natural
* much more