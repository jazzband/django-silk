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

The middleware is placement sensitive. If the middleware before ``silk.middleware.SilkyMiddleware`` returns from ``process_request`` then ``SilkyMiddleware`` will never get the chance to execute. Therefore you must ensure that any middleware placed before never returns anything from ``process_request``. See the `django docs <https://docs.djangoproject.com/en/dev/topics/http/middleware/#process-request>`_ for more information on this.

This `GitHub issue <https://github.com/jazzband/django-silk/issues/12>`_ also has information on dealing with middleware problems.

Garbage Collection
------------------

To `avoid <https://github.com/jazzband/django-silk/issues/265>`_ `deadlock <https://github.com/jazzband/django-silk/issues/294>`_ `issues <https://github.com/jazzband/django-silk/issues/371>`_, you might want to decouple silk's garbage collection from your webserver's request processing, set ``SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT=0`` and trigger it manually, e.g. in a cron job:

.. code-block:: bash
    python manage.py silk_request_garbage_collect
