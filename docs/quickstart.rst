Quick Start
===========

Silk is installed like any other Django app.

First install via pip:

.. code-block:: bash

	pip install django-silk

Add the following to your ``settings.py``:

.. code-block:: python
	
	MIDDLEWARE = [
	    ...
	    'silk.middleware.SilkyMiddleware',
	    ...
	]

	INSTALLED_APPS = (
	    ...
	    'silk'
	)

Add the following to your ``urls.py``:

.. code-block:: python
	
	urlpatterns += patterns('', url(r'^silk', include('silk.urls', namespace='silk')))

Run ``syncdb`` to create Silk's database tables:

.. code-block:: python

    python manage.py syncdb

And voila! Silk will begin intercepting requests and queries which you can inspect by visiting ``/silk/``

Other Installation Options
--------------------------

You can download a release from `github <https://github.com/jazzband/django-silk/releases>`_ and then install using pip:

.. code-block:: bash

	pip install django-silk-<version>.tar.gz

You can also install directly from the github repo but please note that this version is not guaranteed to be working:

.. code-block:: bash

	pip install -e git+https://github.com/jazzband/django-silk.git#egg=silk
