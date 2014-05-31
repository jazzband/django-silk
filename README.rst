=====
Silky
=====

Silky smooth profiling for Django

Quick start
-----------

1. Add "silk" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'silk',
    )

2. Include the silk URLconf in your project urls.py like this::

    url(r'^silk/', include('silk.urls')),

3. Run `python manage.py syncdb` to create the silk models.

4. Start the development server and visit http://127.0.0.1:8000/silk/
