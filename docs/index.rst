.. silk documentation master file, created by
   sphinx-quickstart on Sun Jun 22 13:51:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Silk
================================

.. toctree::
   :maxdepth: 2

   quickstart
   profiling
   configuration
   troubleshooting

Silk is a live profiling and inspection tool for the Django framework. Silk intercepts and stores HTTP requests and database queries before presenting them in a user interface for further inspection:

.. image:: /images/1.png

A **live demo** is available `here`_.

.. _here: http://mtford.co.uk/silk/

Features
--------

- Inspect HTTP requests and responses

  - Query parameters

  - Headers

  - Bodies

  - Execution Time

  - Database Queries

    - Number

    - Time taken

- SQL query inspection

- Profiling of arbitrary code blocks via a Python context manager and decorator

  - Execution Time

  - Database Queries

  - Can also be injected dynamically at runtime e.g. if read-only dependency.

- Authentication/Authorisation for production use


Requirements
------------

* Django: 3.2, 4.2, 5.0
* Python: 3.8, 3.9, 3.10
