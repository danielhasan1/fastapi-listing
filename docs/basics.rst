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
layer. Its use is popular in Java but it has many advantages that anyone can leverage while writing complex reusable data access logics.
The main idea is to separate your business logic from your data access logic.

Benefits

* A dedicated place for writing queries
* Better Separation
* Ability to change queries independently
* Maintain open/close principle
* A common playground when multiple collaborators are working together

Metaphorically "a dedicated place where you cultivate your ingredients for cooking purpose" (stolen from sqlalchemy docs)

For more information click on the above link.

FastAPI Listing uses single table Dao. Each dao class will be bound with single orm model class.

Dao objects
^^^^^^^^^^^

.. py:class:: abstracts.DaoAbstract

The **DaoAbstract** is an abstract base ``class``. ``GenericDao`` extends this abstract ``class``.
when creating dao ``class`` extend ``GenericDao`` which comes with basic necessary setup.
Each Dao object support two protected (limiting their scope to dao layer only) session attributes.
Initiation of any of these attributes is completely up to users.

``_read_db`` and ``_write_db``

You can use these attributes to communicate with the database. You don't have to worry about it too much at the moment.
Just remember these 📝 and their power will be unleashed in tutorial section. Doesn't matter if you have single db or multiple db
or read/write replicas you can use them with this library.

Dao class attributes
^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: GenericDao.model

    The sqlalchemy model class. Attribute type - **Required**

.. py:attribute:: GenericDao.name

    User defined name of dao class, should be unique. Attribute type - **Required**


The Strategy layer (Components)
-------------------------------

Strategy layer is very powerful design pattern that solves various designing problems like how would you design your classes or how would you
maintain multiple algorithm to achieve something at code level or even maintaining open/close **SOLID Design** principles.
Apart from some of the pros like having the need to write boilerplate code and maybe writing a little bit extra depending on your own coding style
the cons it offers are worth using this pattern into your applications.

What you can do?

* You can define independent building blocks of your feature.
* Choice to write atomic level definitions or collection of algorithms handled by inplace client.
* I've personally produced less error prone code with the help of this by writing single responsibility code blocks.
* Easy to write new versions or extend existing strategies.📝

And many more, but we are not here to explore the possibilities of strategy pattern I can only tell you one thing use it if you can it will make life
easier for you and for people who collaborate on your project.

And Just like that lets explore the building blocks using strategy pattern:

Query Strategy
^^^^^^^^^^^^^^

Logical layer to decide on a listing query in a context. By default comes with a ``default_query`` strategy which generates a
``select a,b,c,d from some_table`` query using sqlalchemy where a,b,c,d are columns provided by *client*.

*A client here is someone who consumes query strategy it could be defined at service layer (place to write business logic)
or could be inplace client(existing on strategy layer itself)*

For simple use cases this gets the work done.

.. py:class:: abstracts.QueryStrategy

An abstract base class containing an abstractmethod ``get_query`` this class will act as base for all QueryStrategy classes.

Default implementation of `QUERY STRATEGY`::

    from fastapi_listing.strategies import QueryStrategy

The above default strategy won't do?

After creating your dao class by extending ``GenericDao`` overwrite method ``get_default_read``, and write your sql query. Allows a little flexibility.

**Note: Don't add any behaviour at Dao level, Dao layer should be as generic as possible maintain getter setter behaviour at this Dao**

Feeling like adding a little bit of behaviour like adding logged-in user related API checks?

This is a good indication of creating context specific strategy to get listing query.

Example: You have an employee table and hierarchy Director*->Assistant Director*->Division Managers*->Managers*->Leads*->teams.

You need to design an API to show list of employees associated to logged-in user only. For the sake of this example lets focus on query part for now.

Creating context related query strategies:

``class DirectorQuery(QueryStrategy)``

``class AssistantDirectorQuery(QueryStrategy)``

``class DivisionManagerQuery(QueryStrategy)``

``class ManagersQuery(QueryStrategy)``

``class LeadsQuery(QueryStrategy)``

We won't go so far as to implementing these strategies as that is out of scope of this section.

Benefit of above approach:

- Context is clear by just a look
- light weight containers of logical instructions
- Decoupled and easy to extend
- Define fundamental behaviour in each class
- Much Easier to incorporate new features without breaking existing one by easy extensibility due to such design principle.

Sorting Strategy
^^^^^^^^^^^^^^^^

Responsible for applying sorting scheme(sql native sorting) on your query. Simple as it sounds nothing fancy here.

.. py:class:: abstracts.AbsSortingStrategy

An abstract base class containing an abstractmethod ``sort`` this class acts as base for all SortingStrategy classes

Default implementation of `Sorting Strategy`::

    from fastapi_listing.strategies import SortingOrderStrategy

The **SortingOrderStrategy** ``class`` knows two *client* site keywords ``asc`` or ``dsc`` and applies sorting scheme on basis of this. 📝

*client here is remote client. Its a good time to mention, we have adapters in place to adapt our existing remote client params and convert them to feed into `fastapi-listing`.
so no need to change anything at your remote client site like your frontend or any other backend service*


Pagination Strategy
^^^^^^^^^^^^^^^^^^^

listing query is implicitly shared and a page response that will be returned to remote client is produced.
The default implementation is easy and flexible.

.. py:class:: abstracts.AbsPaginatingStrategy

An abstract base class containing ab abstractmethod ``paginate`` this class acts as base for all PaginatingStrategy classes

Default implementation of `Paginating Strategy`::

    from fastapi_listing.strategies import PaginationStrategy


The Filters layer
^^^^^^^^^^^^^^^^^

The most used feature of any listing service easily, and maintaining filters is an art in itself.

Easily the most complex and sensitive area of any listing that gets out of control in terms of performance as well as readability with poorly maintained code.
Not only talking about simple filters but writing and maintaining the most complex filter is never been easier.
Inspired by **django-admin** design of writing and maintaining filters which
giving you complete control over your filter definitions and their manipulations. Create filter anywhere import it use it like any independent
facade API. As you will see how inbuilt ``generic_filters`` will make it easy and super fast to integrate filters in your listing APIs.


The Interceptor layer
^^^^^^^^^^^^^^^^^^^^^

Allows user to alter the way filters and sorters are applied. Break through the ordinary iterative approach. Implement your own custom
behaviour of execution plan of filters/Sorters.

Reason of existence - In my personal experience there are situations when applying two or many filters directly could cause
multitude of problems if applied in one by one fashion like **django-admin** does. Maybe you wanna skip one or combine two filter into one
and form a more optimised and robust query for your db to handle. You can consider similar scenarios for sorters.

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
