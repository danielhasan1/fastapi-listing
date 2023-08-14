The Basics
==========

Installation
------------

To install FastAPI Listing, run:

.. code-block:: bash

    pip install fastapi-listing


.. _dao overview:


The Dao (Data Access Object) layer
----------------------------------

FastAPI Listing uses a `dao <https://www.oracle.com/java/technologies/data-access-object.html#:~:text=The%20Data%20Access%20Object%20(or,to%20a%20generic%20client%20interface>`_
layer.

Benefits

* A dedicated place for writing queries
* Better Separation
* Ability to change queries independently
* Provides common code usage for more than one place
* imports look cleaner

Metaphorically "a dedicated place where you cultivate your ingredients for cooking purpose" (stolen from sqlalchemy docs)

FastAPI Listing uses single table Dao. Each dao class will be bound with single orm model class 📝.

Dao objects
^^^^^^^^^^^

.. py:class:: GenericDao

when creating dao ``class`` extend ``GenericDao`` which comes with necessary setup code.
Each Dao object support two protected (limiting their scope to dao layer only) session attributes.

``_read_db`` and ``_write_db``

You can use these attributes to communicate with the database. Provides early preparation of when you might need to implement master slave architecture.
Non master slave arch users can point both of these attributes to same db as well. It's simple.

Dao class attributes
^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: GenericDao.model

    The sqlalchemy model class. Attribute type - **Required**

.. py:attribute:: GenericDao.name

    User defined name of dao class, should be unique. Attribute type - **Required**


The Strategy layer
-------------------
Encapsulates process of:
* writing data fetch logics  (Query Strategy)
* applying sorting(if any) after fetching data (Sorting Strategy)
* paginating data at the end (Paginating Strattegy)

Inspiration of using strategy pattern for this:
Depending upon logged in user/applied query filter/performance requirement/legacy based database schema(poorly managed)/data visual limiting due to maybe role of user.
You will write multiple ways to prepare queries to fetch data, or different technique to handle sorting, or a lazy paginator etc.
In any case this is a really good way to handle multiple logic implementations and their compositions.

Query Strategy
^^^^^^^^^^^^^^

Logical layer to decide on a listing query in a context. By default comes with a ``default_query`` strategy which generates a
``select a,b,c,d from some_table`` query using sqlalchemy where a,b,c,d are columns given by the user.

.. _querybasics:

For simple use cases this gets the work done.

.. py:class:: QueryStrategy

You can easily create your custom Query Strategy by extending base class.

➡️ Taking a real world example where using strategy pattern can be helpful:

You have an employee table and hierarchy Director*->Assistant Director*->Division Managers*->Managers*->Leads*->teams.

You need to design an API to show list of employees associated to logged-in user only. For the sake of this example lets focus on query part only.

With strategy you have two ways of achieving this.

➡️ Creating context related query strategies:

``class DirectorQueryForEmp(QueryStrategy)``

``class AssistantDirectorQueryForEmp(QueryStrategy)``

``class DivisionManagerQueryForEmp(QueryStrategy)``

``class ManagersQueryForEmp(QueryStrategy)``

``class LeadsQueryForEmp(QueryStrategy)``

You can abstract and encapsulate relevant logic to make a decision on logged in user basis. You can choose which one to call at runtime.

Or

➡️ Encapsulate the whole thing into one:

``class EmployeeQuery(QueryStrategy)``

And implement context based logics in one place. Choosing to write in any of above style is a personal decision based on project requirements.


Benefit of above approach:

- Context is clear by just a look
- light weight containers of logical instructions
- Decoupled and easy to extend
- Much Easier to incorporate new relevant features like adding for new role or super user.

Sorting Strategy
^^^^^^^^^^^^^^^^

Responsible for applying sorting scheme(sql native sorting) on your query. Simple as it sound, nothing fancy here.

.. py:class:: SortingOrderStrategy

**SortingOrderStrategy** ``class`` knows two *client* site keywords ``asc`` or ``dsc`` and applies sorting scheme on basis of this 📝.

🤯You are using different keywords to make sorting decision? No worries 😉 :ref:`Make FastAPI Listing adapt to it<adapterbenefit>`.


Paginator Strategy
^^^^^^^^^^^^^^^^^^^

Simple Paginator to paginate your database queries and return paginated response to your clients.

.. py:class:: PaginationStrategy

* Easily define pagination params.
* Support dynamic page resizing.
* You can configure ``default_page_size`` to return default number of items if client made a request without pagination params
* You can configure ``max_page_size``, to avoid memory choke on absurd page size demands from clients.
* Easily implement your own custom paginator to add more features like lazy loading or range based slicing.

🤯You have an existing set of pagination params. can you still use it? Yes! 😉 :ref:`Make FastAPI Listing adapt to it<adapterbenefit>`.

The Filters layer
^^^^^^^^^^^^^^^^^

The most used feature of any listing service easily, and maintaining filters is an art in itself ❤️.

Abstracts away the complex procedure of applying filters, No more branching (if else) in your listing API even if you have more than a dozen filters,
with this you can write performance packed robust filters.

Inspired by **django-admin** design of writing and maintaining filters. Create filter anywhere easy to import ❤️ like any independent
facade API. You will see how inbuilt ``generic_filters`` will make it easy and super fast to integrate filters in your listing APIs.

🤯 Can it support your existing clients filter parameters? Ofcourse! 😉 :ref:`Make FastAPI Listing adapt to it<adapterbenefit>`.

.. _intereptorbasics:

The Interceptor layer
^^^^^^^^^^^^^^^^^^^^^

Allows users to write custom execution plan for filters/Sorters.

* Default filter execution plan follows iterative approach when one or more filters are applied by clients.
* Default sorter execution plan allows sort on one param at a time.

Reason of existence❓️ - In my personal experience there are special situations when applying two or many filters directly could cause
multitude of problems if applied in one by one iterative fashion. Maybe you wanna skip one or combine two filter into one
and form a more optimised and robust query for your db to avoid performance hiccups.

Or

Allow sorting on more than one field at a time (I personally don't like the idea as for larger tables it degrades the performance) The best way in my humble opinion
is to shorten your data via filters and then sort on your will.

So now you know you can intercept the way filters and sorters are applied and add your custom behaviours to it.

.. _adapterbenefit:

Params Adapter layer
^^^^^^^^^^^^^^^^^^^^

Everyone implements filter/sorter/paginator layers at their client site differently. For example stackoverflow🧐:

.. image:: https://drive.google.com/uc?export=view&id=1X1DiX7zRhnmJfw-t71Vgk4jnKVIExJzP
  :width: 500
  :alt: Stockoverflow client site params study

You might have a different approach, which is perfectly fine. This is where you can use FastAPI Listing to adjust to the
parameters of your client's site by utilizing ``CoreListingParamsAdapter`` 🤓. With this, you can access your HTTP request
object and parse the query parameters in a way that FastAPI Listing can comprehend.

FastAPI Listing uses ``sort``, ``filter`` and ``pagination`` as keys for the adapter. The adapter should then return the
translated parameters signaled at the native level.

Now, you may wonder how FastAPI Listing natively understands the mentioned parameters:

- Filter: ``[{"field": "<your_field>", "value": {"search": "<your_value>"}}]`` - This represents a list of filters applied by clients, where multiple filters can be applied simultaneously.
- Sort: ``[{"field": "<your_field>", "type": "<asc or dsc>"}]`` - This indicates a list of sorting instructions. While the default supports single sorting (as explained above), customization is possible.
- Pagination: ``{"pageSize": "<integer pagesize>", "page": "<integer page number>"}`` - These are pagination parameters that support dynamic resizing of the page.

This feature proves immensely beneficial for user with  existing operational services seeking an enhanced solution to manage
their current codebase. By leveraging this library, user can potentially integrate it without necessitating modificatin to their remote client
site code. Consequently, FastAPI Listing Service can seamlessly adapt to their requirements.

Moreover, Filters also provide varying semantics for parameters based on ranges and list.


Conclusion
----------

That's it folks that's all for the theory. If you were able to come this far I believe you have a basic understanding of all the components.
In the next section we will start with Tutorials.
