.. fastapi-listing documentation master file, created by
   sphinx-quickstart on Thu May 25 18:05:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fastapi-listing documentation!
=========================================

FastAPI Listing is a data listing library that sits on top of `FastAPI <https://fastapi.tiangolo.com/lo/>`_
to reduce the effort of writing and maintaining listing APIs, through a small set of composable,
decoupled components rather than one large endpoint function.

Filtering, sorting, pagination, and query construction are each their own **component** with a well
defined contract. Compose the defaults for the common case, or swap any one of them out for a custom
implementation without touching the rest.

It ships with SQLAlchemy support out of the box, but the Filter/Sorter/Paginator/QueryStrategy contracts
are backend-agnostic (see :doc:`query`) - a non-ORM ClickHouse backend ships as a reference implementation
proving the same abstraction works for raw parameterized SQL too, and the same approach extends to other
ORMs or database toolkits.

Features
--------

* **Component-based architecture** - independent, single-responsibility pieces that are easy to create, test, and attach.
* **Fewer bugs by construction** - each component does one thing, so a change in one rarely ripples into the others.
* **No core modules to extend** - customisation happens by writing new components, not by subclassing internals.
* **A predefined set of filters** - inspired by Django admin's approach to writing and maintaining filters; create your own alongside the built-ins.
* **Backward compatibility via adapters** - adapt FastAPI Listing to an existing client's query-param format without changing the client.
* **DAO objects usable anywhere** - import a registered DAO directly wherever you need database access, not just inside a listing endpoint.

Some familiarity with the strategy and adapter patterns, and with SOLID principles generally, will make
this documentation easier to follow, though it isn't required.

The manual
----------

.. toctree::
   :maxdepth: 3

   basics
   tutorials
   advanced_user_guide
