The Basics
==========

Installation
------------

To install FastapiListing, run:

.. code-block:: bash

    pip install fastapi-listing


.. _dao overview:

The Dao (Data Access Object) layer
----------------------------------

FastapiListing uses a `dao <https://www.oracle.com/java/technologies/data-access-object.html#:~:text=The%20Data%20Access%20Object%20(or,to%20a%20generic%20client%20interface>`_
layer although its use is popular in JAVA but it has many advantages that anyone can leverage while writing complex applications data access logics.
The main idea is to separate your business logic from your data access logic.

Benefits

* A dedicated place for writing queries
* Better Separation
* Scope of expansion
* Ability to change queries independently

Metaphorically speaking "a dedicated place where you cultivate your ingredients for cooking purpose" (stolen from sqlalchemy docs)

For more information check out the link.

I'll be using **One table Dao** i.e., bind up individual db table with their respective Dao class.

Dao objects
^^^^^^^^^^^

.. py:class:: abstracts.DaoAbstract

The **DaoAbstract** class is an abstract base class provided with necessary information to build your own Dao class. By extending this I've introduced
a ``GenericDao`` class

.. py:class:: dao.GenericDao(DaoAbstract)

The **GenericDao** class contains basic details like how you would wanna instantiate Dao objects. what minimum generic methods you would be keeping
in a Dao class you could implement them or skip them and implement your original definitions

Dao class attributes
^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: GenericDao.model

    The sqlalchemy model class which represents a table. This is an abstract property that each dao class should have.
    Even if you are creating your own Dao class always extend GenericDao or if you don't want these extra functionality or provide a different
    ``__init__`` implementation extend DaoAbstract.

The Strategy layer (Components)
-------------------------------

This section will cover how strategy pattern powers up building different reusable components with ease. It is divided into smaller
subsections with brief information, each subsection is equivalent to a fundamental building block of any listing service. Each block will contain a default
implementation provided out of the box, a bit naive but they get the work done in straightforward scenarios.

But as you jump into writing more complex strategies you will be writing your own Strategy classes
I advice you to always extend Default Strategy class as I'll be adding more nice features at base class level or use provided abstract base classes
to match real signatures.

Each component talk to each other in an optimised order so no need to make calls from one component to another, just design your components
by extending them with given default definitions or abstract base classes to avoid errors.

Query Strategy
^^^^^^^^^^^^^^

This component is only responsible for getting required base query at runtime. That's it it doesn't need to have any extra knowledge and just
focuses on generating a base query that known what data to fetch from database layer. You don't begin writing query at this level but you
tell where to ask to generate a simple/beautiful/complex/monstrous query.

.. py:class:: abstracts.QueryStrategy

An abstract base class containing an abstractmethod ``get_query`` this class will act as base for all QueryStrategy classes

Default implementation of `QUERY STRATEGY`::

    from fastapi_listing.strategies import QueryStrategy

The **QueryStrategy** class contains a default implementation for fetching base query with the help of dao object.



Sorting Strategy
^^^^^^^^^^^^^^^^

This component is responsible for applying sorting scheme that is whether you want your data in an ascending order
or descending order on basis of a particular column or logic.

.. py:class:: abstracts.AbsSortingStrategy

An abstract base class containing an abstractmethod ``sort`` this class acts as base for all SortingStrategy classes

Default implementation of `Sorting Strategy`::

    from fastapi_listing.strategies import SortingOrderStrategy

The **SortingOrderStrategy** class understands two client site keywords `asc` or `dsc` and applies sorting scheme on basis of this, more information will be
shared in tutorial section

Pagination Strategy
^^^^^^^^^^^^^^^^^^^

This component applies slicing technique on implicitly shared query and prepares a complete page response that will be returned to client.

.. py:class:: abstracts.AbsPaginatingStrategy

.. py:attribute:: default_pagination_params

Default page meta information that will be used in preparing page response.

An abstract base class containing ab abstractmethod ``paginate`` his class acts as base for all PaginatingStrategy classes

Default implementation of `Paginating Strategy`::

    from fastapi_listing.strategies import PaginationStrategy

The **PaginationStrategy** class is responsible for applying default limit offset data slicing strategy. it also supports variable
page size response and default page size.

The Filters layer
^^^^^^^^^^^^^^^^^

The most used feature of any listing service easily and maintaining filters is an art in itself.

Though the ordering of this component should have been between :ref:`Query Strategy` and :ref:`Sorting Strategy` component I intentionally added it here.
This is easily the most complex and sensitive area of any listing that is excepting dynamic client site filter requests.
Not only talking about simple filters but writing and maintaining the most complex filter is never been easier though I won't be sharing
much details here it would be best to show you a working example. The filters are maintained in mini sub component architecture
giving you complete control over your filter definitions and their manipulations. Create filter anywhere import it use it like any independent
API.


The Mechanics layer
^^^^^^^^^^^^^^^^^^^

This is directly related to Sorting and filter component. A client could ask to apply multiple filters or multiple sorts
(though it doesn't make any sense for multi field sort) We may sometime require to alter how multiple filters and sorting gets applied
or when two filter is applied only apply single filter because these two filters are related.

By Default filters are applied in iterative manner and single item sorting is allowed. You could write your own mechanics
to provide a different filter and sorting application or have checks for the sake of query optimisations.

I've worked on many systems where if two filters is applied I needed to alter the behaviour of iterative filter mechanism
or allow bypass for particular set of filters.


Conclusion
----------

That's it folks that's all for the theory. If you were able to come this far I believe you have a basic understanding of all the components.
In the next section we will start with Tutorials.
