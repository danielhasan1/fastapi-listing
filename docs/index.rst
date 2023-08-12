.. fastapi-listing documentation master file, created by
   sphinx-quickstart on Thu May 25 18:05:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fastapi-listing documentation!
=========================================

FastAPI Listing is an advanced data listing library that works on top of `fastAPI <https://fastapi.tiangolo.com/lo/>`_
to reduce the efforts in writing and maintaining your listing APIs by providing
a highly extensible, decoupled and reusable interface.

**Component** based Plug & Play architecture allows you to write easy to use and more **quickly** readable block of code.
Inject dependencies or swap components as you write more and more complex logics.

It uses `SQLAlchemy <https://en.wikipedia.org/wiki/SQLAlchemy>`_ sqltool at the time but have potential to support multiple ORMs/database
toolkits and that will be coming soon like mongoengine 📝.

Features
--------

* **Component Based Architecture**: Small collection of independent instructions. Easy to create and attach.
* **Maintenance**: Fast to code and maintain, Light weight components are easy to create in case of multiple development iteration/customisations.
* **Fewer Bugs**: Reduce the amount of bugs by always having single responsibility modules, Focus on one sub problem at a time to solve the bigger one.
* **Easy**: Designed to be easy to use and never having the need to extend core modules.
* **Short**: Minimize code duplication.
* **Filters**: A predefined set of filters. Create new one or extend existing ones. An approach Inspired by **django admin**. Allows you to write powerful robust and reusable filters.
* **Backport Compatibility**: Level up your existing listing APIs by using FastAPI Listing without changing any client site dependency utilizing adapters.
* **Anywhere Dao objects**: Dao object powered by sqlalchemy sessions are just an import away. Use them anywhere to interact with database.

Having some knowledge of design patterns such as strategy pattern, adapter pattern and solid principles could be a plus going forward in this documentation 📚️.


The manual
----------

.. toctree::
   :maxdepth: 2

   basics
   tutorials


