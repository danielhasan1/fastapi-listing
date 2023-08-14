.. _learnfilters:

Adding Filters to your listing API
----------------------------------

The most interesting part of a listing that becomes the most hated part of any listing super easily.

Starting with an easy request.

Adding a filter that will filter your employee listing on basis of  ``gender``.

.. code-block:: python
    :emphasize-lines: 1, 7

    from fastapi_listing.filters import generic_filters


    @loader.register()
    class EmployeeListingService(ListingService):

        filter_mapper = {
            "gdr": ("Employee.gender", generic_filters.EqualityFilter),
        }

        # rest of the definition is going to be same no change required.

In above example we have imported a module ``generic_filters`` which holds some of the very commonly used query filters supported by FastAPI Listing.
These are highly reusable and support a cross model in place hook when you may wanna provide secondary model field.
There are a bunch of filters out of the box to speed up your regular listing API development.😉



.. list-table::
   :widths: auto

   * - ``EqualityFilter``
     - equality filter ``a == b``
   * - ``InEqualityFilter``
     - inequality filter ``a != b``
   * - ``InDataFilter``
     - ``in`` filter ``a in (b)``
   * - ``BetweenUnixMilliSecDateFilter``
     - best way to avoid conflict between date formate awareness. deal in unix timestamp. range filter ``between(start,end)``
   * - ``StringStartsWithFilter``
     - like filter ``a like b%``
   * - ``StringEndsWithFilter``
     - like filter ``a like %b``
   * - ``StringContainsFilter``
     - contains substring filter ``a like %b%``. recommended use on only small tables
   * - ``StringLikeFilter``
     - string equality filter ``a like b``
   * - ``DataGreaterThanFilter``
     - greater than filter ``a > b``
   * - ``DataGreaterThanEqualToFilter``
     - greater than equal to filter ``a >= b``
   * - ``DataLessThanFilter``
     - less than filter a < b
   * - ``DataLessThanEqualToFilter``
     - less than equal to filter a <= b
   * - ``DataGropByElementFilter``
     - aggregation filter ``a group by b``
   * - ``DataDistinctByElementFilter``
     - distinct data filter ``distinct a``
   * - ``HasFieldValue``
     - has field filter ``a is null`` or ``a is not null``
   * - ``MySqlNativeDateFormateRangeFilter``
     - native date formate range filter between(a,b)


I hope you still remember :ref:`filter_mapper <filter_mapper_label>`

Each item of this mapping dict has 3 key components.

1. the key itself which will be sent in remote client request.
2. The tuple
    * first item is ``model.field`` -> Field associated to primary table. The filter will be applied on it.
    * second item is your filter class definition.

And that's it you have successfully implemented your first filter.


Several benefits of having an alias over your actual fields as shown in the above dict key.
1. You will never expose your actual field name to the remote client which help to secure your service.
2. You will have a more cleaner looking request urls which will only make sense to software developers.
3. It will trim out the extra information exposing from urls.

How FastAPI Listing reads filter params:

* when you have a single value filter - ``[{"field": "alias<(filter mapper dict key)>", "value":{"search":<whatever remote client chose to search>}}]`` 📝
* when you have multi value filter - ``[{"field": "alias<(filter mapper dict key)>", "value":{"list":<whatever remote client chose to search in list>}}]`` 📝
* when you have a range value filter - ``[{"field": "alias<(fileter mapper dict key)>", "value":{"start":<whatever remote client chose to search>, "end":<whatever remote client chose to search>}}]`` 📝

**If you have an existing running service that means you already have running remote client setup that will be sending different named query params for filter, then
use the :ref:`adapter` to make your existing listing service adapt to your existing code.**


Customising your filters
^^^^^^^^^^^^^^^^^^^^^^^^

Using secondary model field. Lets say you wanna use a field from ``DeptEmp`` model. If you give the write your filter like this

.. code-block:: python

    filter_mapper = {
        "gdr": ("Employee.dept_no", generic_filters.EqualityFilter),
    }

it will raise an attribute error which is expected as your primary model doesnt have this field.
We have a rule to only allow a primary model plugged to our listing service.

To allow passing secondary model field

.. code-block:: python
    :emphasize-lines: 2

    filter_mapper = {
        "dpt": ("Employee.DeptEmp.dept_no", generic_filters.EqualityFilter, lambda x: getattr(DeptEmp, x))
    }

Lets see what extra we have in our tuple above.

We have an extra lambda definition which tells what model field to use when this filter gets applied.
As to why I chained two model names ``Employee.DeptEmp.dept_no``?

There is a filter factory which centrally encapsulates all application logic. It works on unique field names(So you can't provide duplicate names).
the **alias(filter mapper dict key)** could be same for multiple listing services and multiple database schema could contain same field names
but any database asks you to provide unique schema(table) name similarly we register the filter under `schema.field` name to reduce for users to always coming
up with random unique names.
Chaining the name like this shows a clear relation that from ``Employee`` to ``DeptEmp`` where field is ``dept_no``.
Though you can argue with it and still choose a different way of adding your filter field. Just make sure it is understandable.

Note that if we use filter with this query strategy :ref:`dept emp query strategy <dept_emp_q_stg>` then only this would work. becuase our base query is aware of
``DeptEmp``.

Writing a custom filter
^^^^^^^^^^^^^^^^^^^^^^^

You wanna write your own filter because FastAPI Listing default filters were unable to fulfill your use case 🥹.

Its easy to do as well. You wanna write a filter which does a full name scan combining first_name and last_name columns.

.. code-block:: python
    :emphasize-lines: 2, 4, 6

    from fastapi_listing.filters import generic_filters
    from fastapi_listing.dao import dao_factory

    class FullNameFilter(generic_filters.CommonFilterImpl):

        def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
            # field is not necessary here as this is a custom filter and user have full control over its implementation
            if value:
                emp_dao: EmployeeDao = dao_factory.create("employee", replica=True)
                emp_ids: list[int] = emp_dao.get_emp_ids_contain_full_name(value.get("search"))
                query = query.filter(self.dao.model.emp_no.in_(emp_ids))
            return query

As you can see in above filter class we are inheriting from a class which is a part of our ``generic_filters`` module.
In our filter class we have a single filter method with fixed signature. you will receive your filter value as a dict.
We have also used **dao factory**  which allows us to use anywhere dao policy.
You basically filter your query and return it.
And just like that voila your custom filter is ready. No need to think how you will call it, this will be handled implicitly by filter mechanics(interceptor).

Why do we need an interceptor? Just bear with this example to have an idea of when you may wanna use or write your own interceptor.

Lets say you have a listing of products and a mapping table where products are mapped to some groups and each group belongs to a bigger group.

Your mapping table looks like this

.. code-block:: sql

    id | product_id | group_id | sub_group_id


You added filters for group sub group and product on your listing. You wrote your custom filters to either apply **lazy join** or resolve mapping data
and then apply the filter. So when:

* A user applies Group filter - Your custom Group Filter gets called.
* A user applies Sub Group filter - Your custom SubGroup Filter gets called with above Group Filter because user hasn't removed above filter.
* A user applies Product filter with above two filters Your Product filter gets called with maybe with existing ``generic_filters.EqualityFilter`` Filter.

Group -> Sub Group -> Product

As the default interceptor runs in an iterative fashion which applies filter one by one you may end up getting different results. Why? lets see:

You may try to find id of products mapped to Group A and applies filter on these ids. Perfect ✅

``select product_id from mapping where group_id = 'A';``

and then feed these product_id into your filter via ``in`` query.

On application of second filter you will repeat above process to find product ids and apply the filter again but wait will you receive sane results? I doubt it. ❌

``select product_id from mapping where sub_group_id = "A_a";``

First your Group Filter is called. It returned product_ids. Then your Sub Group Filter is called and it may return different product_ids
again you will feed these product_ids into your filter via ``in`` query. To avoid this you could create an advanced filter which is combination of both.
Create a custom filter where you could find product_ids with below query

``select product from mapping where group_id = 'A' and sub_group_id = 'A_a';`` ✅

This will give you accurate product_ids. Once you have a custom filter you could detect if these two filters are applied together
and modify their application by combining these two into one.

Hope this gives you a more clear picture of situations where filter interceptor could play a significance role in reducing code complexity and
providing a more cleaner approach towards writing your code.

I've faced situations like this in some system and to resolve such situation interceptor could be a big help.