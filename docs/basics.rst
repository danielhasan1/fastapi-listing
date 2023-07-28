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
layer although its use is popular in Java but it has many advantages that anyone can leverage while writing complex reusable data access logics.
The main idea is to separate your business logic from your data access logic.

Benefits

* A dedicated place for writing queries
* Better Separation
* Scope of expansion
* Ability to change queries independently
* Maintain open/close principle with ease
* A common playground when multiple collaborators are working together

Metaphorically "a dedicated place where you cultivate your ingredients for cooking purpose" (stolen from sqlalchemy docs)

For more information check out the link.

FastAPI Listing uses single table Dao i.e. primary one table will bind with one dao class.

Dao objects
^^^^^^^^^^^

.. py:class:: abstracts.DaoAbstract

The **DaoAbstract** class is an abstract base class. ``GenericDao`` extends this abstract class. All of your dao ``class``
will be extend ``GenericDao`` to have basic Dao functionalities. Each Dao object support two protected (limiting their scope to dao layer only) session attributes.
Initiation of any of these attributes is completely up to users. Namely they are known as ``_read_db`` and ``_write_db``


Dao class attributes
^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: GenericDao.model

    The sqlalchemy model class. Attribute type - Required

.. py:attribute:: GenericDao.name

    User defined name of dao class, should be unique. Attribute type - Required


The Strategy layer (Components)
-------------------------------

This section will cover how strategy pattern powers up building different reusable components with ease. It is divided into smaller
subsections with brief information, each subsection is equivalent to a fundamental building block of any listing service.
I've added a simple implementation that a user could extend and write brand new implementation on their own whenever needed.

But as you jump into writing more complex strategies you will be writing your own Strategy classes
I advice you to always extend Default Strategy class as I'll be adding more nice features at base class level or use provided abstract base classes
to match real signatures.

Each component talk to each other in an optimised order so no need to make calls from one component to another, just design your components
by extending them with given default definitions or abstract base classes to avoid errors.

Query Strategy
^^^^^^^^^^^^^^

This component is only responsible for getting required base query at runtime. That's it it doesn't need to have any extra knowledge and just
focuses on generating a base query that knows what data to fetch from database layer. You don't begin writing query at this level but you
tell where to look to find a simple/beautiful/complex/monstrous query. As this is a behavioural class you could add more personalise information
to the naming convention or class definition, keep associative logics inbound etc.

.. py:class:: abstracts.QueryStrategy

An abstract base class containing an abstractmethod ``get_query`` this class will act as base for all QueryStrategy classes

Default implementation of `QUERY STRATEGY`::

    from fastapi_listing.strategies import QueryStrategy

The **QueryStrategy** class contains a default implementation for fetching base query with the help of dao object.



Sorting Strategy
^^^^^^^^^^^^^^^^

This component is responsible for applying sorting scheme(sql native sorting) on your query. It is as simple as it sounds nothing fancy here.

.. py:class:: abstracts.AbsSortingStrategy

An abstract base class containing an abstractmethod ``sort`` this class acts as base for all SortingStrategy classes

Default implementation of `Sorting Strategy`::

    from fastapi_listing.strategies import SortingOrderStrategy

The **SortingOrderStrategy** class understands two client site keywords ``asc`` or ``dsc`` and applies sorting scheme on basis of this, more information will be
shared in tutorial section

Pagination Strategy
^^^^^^^^^^^^^^^^^^^

This component applies slicing technique on implicitly shared query and prepares a complete page response that will be returned to remote client.
You can change paginating strategy real quick and easily whenever going for query optimization.

.. py:class:: abstracts.AbsPaginatingStrategy


An abstract base class containing ab abstractmethod ``paginate`` this class acts as base for all PaginatingStrategy classes

Default implementation of `Paginating Strategy`::

    from fastapi_listing.strategies import PaginationStrategy

The **PaginationStrategy** class is responsible for applying default limit offset data slicing strategy. it also supports variable
page size response and option to avoid count or provide a dummy count to avoid slow count queries.

The Filters layer
^^^^^^^^^^^^^^^^^

The most used feature of any listing service easily, and maintaining filters is an art in itself.

Easily the most complex and sensitive area of any listing that gets out of control with poorly maintained code.
Not only talking about simple filters but writing and maintaining the most complex filter is never been easier.
The filters are maintained in mini sub component architecture with fixed single responsibility
giving you complete control over your filter definitions and their manipulations. Create filter anywhere import it use it like any independent
facade API.


The Interceptor layer
^^^^^^^^^^^^^^^^^^^^^

Allows user to alter the way filters and sorters are applied. Break through the ordinary iterative approach. Implement your own custom
behaviour of execution plan of filters/Sorters.

Reason of existence - In my personal experience there are situations when applying two or many filters directly could cause
multitude of problems if applied in one by one fashion like **django-admin**. Maybe you wanna skip one or combine two filter into one
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
