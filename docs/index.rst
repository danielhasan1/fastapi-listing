.. fastapi-listing documentation master file, created by
   sphinx-quickstart on Thu May 25 18:05:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fastapi-listing's documentation!
===========================================

FastAPI Listing is an advanced data listing library that works on top of `fastAPI <https://fastapi.tiangolo.com/lo/>`_
to reduce the efforts in writing and maintaining your listing APIs by providing
a highly extendable, decoupled and reusable interface. It lets you avoid recreating, duplicating, and writing unreadable code.

**Design your own generic solutions that can be reused**.

**Component** based Plug & Play architecture allows you to write easy to use, understandable & more **quickly** readable pieces of code.
Inject dependencies or swap components as you write more and more complex logics. **Components** follow **single responsibility principle**
that improves **cohesion** and overall much cleaner composition of code blocks.

It uses `SQLAlchemy <https://en.wikipedia.org/wiki/SQLAlchemy>`_ sqltool at the time but have potential to support multiple ORMs/database
toolkits and that will be coming soon.

Change/Extend/Write-new-versions of what you need, when you need, with components based architecture it is possible with ease.

Features
--------

* **Component Based Architecture**: Small collection of independent instructions. Easy to create and attach.
* **Maintenance**: Fast to code and maintain, Light weight components are easy to maintain in case of multiple development iteration/customisations.
* **Fewer Bugs**: Reduce the amount of bugs by always having single responsibility modules, Focus on one sub problem at a time to solve the bigger one.
* **Easy**: Designed to be easy to use and never having the need to extend core modules.
* **Short**: Minimize code duplication. Unlimited scope of creating reusable components/features.
* **Swappable Components**: As components are independent you can write new components, extend existing components.
* **Filters**: A predefined set of filters. Create new one or extend existing ones. An approach Inspired by **django admin**. Allows you to write really robust and reusable filters.
* **Backport Compatibility**: Level up your existing listing APIs by using FastAPI Listing without changing any client site dependency by adding your own *adapters*.
* **Anywhere Dao Session**: Use dao session anywhere and everywhere in your code with single import.

We use strategy pattern at its core so if you don't know anything about it please have a look at `here <https://en.wikipedia.org/wiki/Strategy_pattern>`_
as a prerequisite.


Switch between different strategies on the fly, master the art of writing generic solutions that you could reuse and unleash the full potential
of this advanced listing library. The best part is **Users gain full access in designing there components and taking decisions to write logics as per their API
needs having complete control over all integral logics and their behaviours**.

The manual
----------

.. toctree::
   :maxdepth: 2

   basics
   tutorials


