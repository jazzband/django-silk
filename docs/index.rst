.. silk documentation master file, created by
   sphinx-quickstart on Sun Jun 22 13:51:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Silk
================================

Contents:

.. toctree::
   :maxdepth: 2

   profiling

Silk is a live profiling and inspection tool for the Django framework. Silk can:

- Intercept HTTP requests and responses for further inspection
- Time execution of requests
- Intercept database queries per request
- Profile blocks of code 
	- Timing
	- Database queries

A live demo is available at http://mtford.co.uk/silk/.

Requirements
------------

* Django: 1.5, 1.6
* Python: 2.7, 3.3, 3.4