=====
Silky
=====

Silky smooth profiling for Django

Quick start
-----------

1. Add "silky" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'silky',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^silky/', include('silky.urls')),

3. Run `python manage.py syncdb` to create the silky models.

4. Start the development server and visit http://127.0.0.1:8000/silky/
