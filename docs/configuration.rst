Configuration
======

Authentication/Authorisation
----

By default anybody can access the Silk user interface by heading to `/silk/`. To enable your Django 
auth backend place the following in `settings.py`:


.. code-block:: python

	SILKY_AUTHENTICATION = True  # User must login
	SILKY_AUTHORISATION = True  # User must have permissions

If ``SILKY_AUTHORISATION`` is ``True``, by default Silk will only authorise users with ``is_staff`` attribute set to ``True``.

You can customise this using the following in ``settings.py``:

.. code-block:: python

	def my_custom_perms(user):
	    return user.is_allowed_to_use_silk

	SILKY_PERMISSIONS = my_custom_perms


Request/Response bodies
----

By default, Silk will save down the request and response bodies for each request for future viewing
no matter how large. If Silk is used in production under heavy volume with large bodies this can have
a huge impact on space/time performance. This behaviour can be configured with following options:

.. code-block:: python

	SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
	SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # If response body>1024kb, ignore


Meta-Profiling
-----

Sometimes its useful to be able to see what effect Silk is having on the request/response time. To do this add
the following to your `settings.py`:

.. code-block:: python

	SILKY_META = True

Silk will then record how long it takes to save everything down to the database at the end of each request:

.. image:: meta.png

Note that in the above screenshot, this means that the request took 29ms (22ms from Django and 7ms from Silk)