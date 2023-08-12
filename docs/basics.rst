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


The Interceptor layer
^^^^^^^^^^^^^^^^^^^^^

Allows user to alter the way filters and sorters are applied. Basically allows users to write custom execution plan for filters/Sorters.

Reason of existence - In my personal experience there are situations when applying two or many filters directly could cause
multitude of problems if applied in one by one fashion like **django-admin** does. Maybe you wanna skip one or combine two filter into one
and form a more optimised and robust query for your db to handle. You can consider similar scenarios for sorters.

.. _adapterbenefit:

The Feature Params Adapter layer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Allows user to write interface that transform remote client site incompatible objects(http requests params) to be adaptable by
FastAPI Listing package. Extremely helpful for users who have running services and looking for a better solution to
manage their existing codebase.
This could allow them to use this library without the need to change their remote client site code and allow FastAPI Listing Service to adapt to their need.

Conclusion
----------

That's it folks that's all for the theory. If you were able to come this far I believe you have a basic understanding of all the components.
In the next section we will start with Tutorials.
