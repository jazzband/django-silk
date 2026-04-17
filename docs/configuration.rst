Configuration
=============

Authentication and Authorisation
--------------------------------

**Silk is locked down by default.** Unauthenticated requests, and authenticated
requests from users without ``is_staff=True``, receive a ``404 Not Found`` from
every ``/silk/…`` URL — as if the app weren't mounted. This avoids
accidentally shipping an unauthenticated profiling UI to production.

To expose the UI publicly (for example in a fully-internal dev environment),
disable both flags:

.. code-block:: python

    SILKY_AUTHENTICATION = False
    SILKY_AUTHORISATION = False

To customise *which* authenticated users see the UI, replace the default
predicate (``user.is_staff``) with your own:

.. code-block:: python

    def my_custom_perms(user):
        return user.is_allowed_to_use_silk

    SILKY_PERMISSIONS = my_custom_perms

.. note::

    Silk returns 404 (not 403) on unauthorised access so that the UI's
    existence can't be fingerprinted by an anonymous probe. Static assets
    under ``/static/silk/…`` are not covered by this — if you serve them
    through nginx, whitenoise, or similar, restrict them at your edge for
    full opacity.


Request and Response bodies
---------------------------

By default, Silk will save down the request and response bodies for each request for future viewing
no matter how large. If Silk is used in production under heavy volume with large bodies this can have
a huge impact on space/time performance. This behaviour can be configured with following options:

.. code-block:: python

	SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
	SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # If response body>1024kb, ignore


Meta-Profiling
--------------

Sometimes its useful to be able to see what effect Silk is having on the request/response time. To do this add
the following to your `settings.py`:

.. code-block:: python

	SILKY_META = True

Silk will then record how long it takes to save everything down to the database at the end of each request:

.. image:: /images/meta.png

Note that in the above screenshot, this means that the request took 29ms (22ms from Django and 7ms from Silk)

Limiting request and response data
----------------------------------

To make sure silky garbage collects old request/response data, a config var can be set to limit the number of request/response rows it stores.

.. code-block:: python

    SILKY_MAX_RECORDED_REQUESTS = 10**4

The garbage collection is only run on a percentage of requests to reduce overhead.  It can be adjusted with this config:

.. code-block:: python

    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10
