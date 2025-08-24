Troubleshooting
===============

The below details common problems when using Silk, most of which have been derived from the solutions to github issues.

Unicode
-------

Silk saves down the request and response bodies of each HTTP request by default. These bodies are often UTF encoded and hence it is important that Silk's database tables are also UTF encoded. Django has no facility for enforcing this and instead assumes that the configured database defaults to UTF.

If you see errors like:


	Incorrect string value: '\xCE\xBB, \xCF\x86...' for column 'raw_body' at row...


Then it's likely your database is not configured correctly for UTF encoding.

See this `github issue <https://github.com/jazzband/django-silk/issues/21>`_ for more details and workarounds.

Middleware
----------

The order of middleware is sensitive. If any middleware placed before ``silk.middleware.SilkyMiddleware`` returns a response without invoking its ``get_response``, the ``SilkyMiddleware`` won’t run. To avoid this, ensure that middleware preceding ``SilkyMiddleware`` does not bypass or return a response without calling its ``get_response``. For further details, check out the `Django documentation <https://docs.djangoproject.com/en/dev/topics/http/middleware/#middleware-order-and-layering>`.

Garbage Collection
------------------

To `avoid <https://github.com/jazzband/django-silk/issues/265>`_ `deadlock <https://github.com/jazzband/django-silk/issues/294>`_ `issues <https://github.com/jazzband/django-silk/issues/371>`_, you might want to decouple silk's garbage collection from your webserver's request processing, set ``SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT=0`` and trigger it manually, e.g. in a cron job:

.. code-block:: bash

    python manage.py silk_request_garbage_collect
