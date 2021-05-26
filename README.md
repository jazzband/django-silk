# Silk

[![GitHub Actions](https://github.com/jazzband/django-silk/workflows/Test/badge.svg)](https://github.com/jazzband/django-silk/actions)
[![GitHub Actions](https://codecov.io/gh/jazzband/django-silk/branch/master/graph/badge.svg)](https://codecov.io/gh/jazzband/django-silk)
[![PyPI Download](https://img.shields.io/pypi/v/django-silk.svg)](https://pypi.python.org/pypi/django-silk)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/django-silk.svg)](https://pypi.python.org/pypi/django-silk)
[![Supported Django versions](https://img.shields.io/pypi/djversions/django-silk.svg)](https://pypi.python.org/pypi/django-silk)
[![Jazzband](https://jazzband.co/static/img/badge.svg)](https://jazzband.co/)

Silk is a live profiling and inspection tool for the Django framework. Silk intercepts and stores HTTP requests and database queries before presenting them in a user interface for further inspection:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/1.png" width="720px"/>

**SECURITY NOTE:** Because Silk stores all HTTP requests into the database in plain text, it will store the request's sensitive information into the database _in plain text_ (e.g. users' passwords!). This is a massive security concern. An issue has been created for this [here](https://github.com/jazzband/django-silk/issues/305).

## Contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Features](#features)
* [Configuration](#configuration)
  * [Authentication/Authorisation](#authenticationauthorisation)
  * [Request/Response bodies](#requestresponse-bodies)
  * [Meta-Profiling](#meta-profiling)
  * [Recording a fraction of requests](#recording-a-fraction-of-requests)
  * [Limiting request/response data](#limiting-requestresponse-data)
  * [Clearing logged data](#clearing-logged-data)
* [Contributing](#contributing)
  * [Development Environment](#development-environment)

## Requirements

Silk has been tested with:

* Django: 2.2, 3.0, 3.1, 3.2
* Python: 3.6, 3.7, 3.8, 3.9

## Installation

Via pip into a `virtualenv`:

```bash
pip install django-silk
```

In `settings.py` add the following:

```python
MIDDLEWARE = [
    ...
    'silk.middleware.SilkyMiddleware',
    ...
]

INSTALLED_APPS = (
    ...
    'silk'
)
```

**Note:** The middleware placement is sensitive. If the middleware before `silk.middleware.SilkyMiddleware` returns from `process_request` then `SilkyMiddleware` will never get the chance to execute. Therefore you must ensure that any middleware placed before never returns anything from `process_request`. See the [django docs](https://docs.djangoproject.com/en/dev/topics/http/middleware/#process-request) for more information on this.

**Note:** If you are using `django.middleware.gzip.GZipMiddleware`, place that **before** `silk.middleware.SilkyMiddleware`, otherwise you will get an encoding error.

If you want to use custom middleware, for example you developed the subclass of `silk.middleware.SilkyMiddleware`, so you can use this combination of settings:

```python
# Specify the path where is the custom middleware placed
SILKY_MIDDLEWARE_CLASS = 'path.to.your.middleware.MyCustomSilkyMiddleware'

# Use this variable in list of middleware
MIDDLEWARE = [
    ...
    SILKY_MIDDLEWARE_CLASS,
    ...
]
```

To enable access to the user interface add the following to your `urls.py`:

```python
urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
```

before running migrate:

```bash
python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic
```


Silk will automatically begin interception of requests and you can proceed to add profiling
if required. The UI can be reached at `/silk/`

### Alternative Installation

Via [github tags](https://github.com/jazzband/django-silk/releases):

```bash
pip install https://github.com/jazzband/silk/archive/<version>.tar.gz
```

You can install from master using the following, but please be aware that the version in master
may not be working for all versions specified in [requirements](#requirements)

```bash
pip install -e git+https://github.com/jazzband/django-silk.git#egg=silk
```

## Features

Silk primarily consists of:

* Middleware for intercepting Requests/Responses
* A wrapper around SQL execution for profiling of database queries
* A context manager/decorator for profiling blocks of code and functions either manually or dynamically.
* A user interface for inspection and visualisation of the above.

### Request Inspection

The Silk middleware intercepts and stores requests and responses in the configured database.
These requests can then be filtered and inspecting using Silk's UI through the request overview:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/1.png" width="720px"/>

It records things like:

* Time taken
* Num. queries
* Time spent on queries
* Request/Response headers
* Request/Response bodies

and so on.

Further details on each request are also available by clicking the relevant request:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/2.png" width="720px"/>

### SQL Inspection

Silk also intercepts SQL queries that are generated by each request. We can get a summary on things like
the tables involved, number of joins and execution time (the table can be sorted by clicking on a column header):

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/3.png" width="720px"/>

Before diving into the stack trace to figure out where this request is coming from:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/5.png" width="720px"/>

### Profiling

Turn on the SILKY_PYTHON_PROFILER setting to use Python's built-in cProfile profiler. Each request will be separately profiled and the profiler's output will be available on the request's Profiling page in the Silk UI.

```python
SILKY_PYTHON_PROFILER = True
```

If you would like to also generate a binary `.prof` file set the following:

```python
SILKY_PYTHON_PROFILER_BINARY = True
```

When enabled, a graph visualisation generated using [gprof2dot](https://github.com/jrfonseca/gprof2dot) and [viz.js](https://github.com/almende/vis) is shown in the profile detail page:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/10.png" width="720px"/>


A custom storage class can be used for the saved generated binary `.prof` files:

```python
SILKY_STORAGE_CLASS = 'path.to.StorageClass'
```

The default storage class is `silk.storage.ProfilerResultStorage`, and when using that you can specify a path of your choosing. You must ensure the specified directory exists.

```python
# If this is not set, MEDIA_ROOT will be used.
SILKY_PYTHON_PROFILER_RESULT_PATH = '/path/to/profiles/'
```

A download button will become available with a binary `.prof` file for every request. This file can be used for further analysis using [snakeviz](https://github.com/jiffyclub/snakeviz) or other cProfile tools


Silk can also be used to profile specific blocks of code/functions. It provides a decorator and a context
manager for this purpose.

For example:

```python
from silk.profiling.profiler import silk_profile


@silk_profile(name='View Blog Post')
def post(request, post_id):
    p = Post.objects.get(pk=post_id)
    return render_to_response('post.html', {
        'post': p
    })
```

Whenever a blog post is viewed we get an entry within the Silk UI:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/7.png" width="720px"/>

Silk profiling not only provides execution time, but also collects SQL queries executed within the block in the same fashion as with requests:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/8.png" width="720px"/>

#### Decorator

The silk decorator can be applied to both functions and methods

```python
from silk.profiling.profiler import silk_profile


# Profile a view function
@silk_profile(name='View Blog Post')
def post(request, post_id):
    p = Post.objects.get(pk=post_id)
    return render_to_response('post.html', {
        'post': p
    })


# Profile a method in a view class
class MyView(View):
    @silk_profile(name='View Blog Post')
    def get(self, request):
        p = Post.objects.get(pk=post_id)
        return render_to_response('post.html', {
            'post': p
        })
```

#### Context Manager

Using a context manager means we can add additional context to the name which can be useful for
narrowing down slowness to particular database records.

```python
def post(request, post_id):
    with silk_profile(name='View Blog Post #%d' % self.pk):
        p = Post.objects.get(pk=post_id)
        return render_to_response('post.html', {
            'post': p
        })
```

#### Dynamic Profiling

One of Silk's more interesting features is dynamic profiling. If for example we wanted to profile a function in a dependency to which we only have read-only access (e.g. system python libraries owned by root) we can add the following to `settings.py` to apply a decorator at runtime:

```python
SILKY_DYNAMIC_PROFILING = [{
    'module': 'path.to.module',
    'function': 'MyClass.bar'
}]
```

which is roughly equivalent to:

```python
class MyClass(object):
    @silk_profile()
    def bar(self):
        pass
```

The below summarizes the possibilities:

```python

"""
Dynamic function decorator
"""

SILKY_DYNAMIC_PROFILING = [{
    'module': 'path.to.module',
    'function': 'foo'
}]

# ... is roughly equivalent to
@silk_profile()
def foo():
    pass

"""
Dynamic method decorator
"""

SILKY_DYNAMIC_PROFILING = [{
    'module': 'path.to.module',
    'function': 'MyClass.bar'
}]

# ... is roughly equivalent to
class MyClass(object):

    @silk_profile()
    def bar(self):
        pass

"""
Dynamic code block profiling
"""

SILKY_DYNAMIC_PROFILING = [{
    'module': 'path.to.module',
    'function': 'foo',
    # Line numbers are relative to the function as opposed to the file in which it resides
    'start_line': 1,
    'end_line': 2,
    'name': 'Slow Foo'
}]

# ... is roughly equivalent to
def foo():
    with silk_profile(name='Slow Foo'):
        print (1)
        print (2)
    print(3)
    print(4)
```

Note that dynamic profiling behaves in a similar fashion to that of the python mock framework in that
we modify the function in-place e.g:

```python
""" my.module """
from another.module import foo

# ...do some stuff
foo()
# ...do some other stuff
```

,we would profile `foo` by dynamically decorating `my.module.foo` as opposed to `another.module.foo`:

```python
SILKY_DYNAMIC_PROFILING = [{
    'module': 'my.module',
    'function': 'foo'
}]
```

If we were to apply the dynamic profile to the functions source module `another.module.foo` **after**
it has already been imported, no profiling would be triggered.


#### Custom Logic for Profiling

Sometimes you may want to dynamically control when the profiler runs. You can write your own logic for when to enable the profiler. To do this add the following to your `settings.py`:

This setting is mutually exclusive with SILKY_PYTHON_PROFILER and will be used over it if present. It will work with SILKY_DYNAMIC_PROFILING.

```python
def my_custom_logic(request):
    return 'profile_requests' in request.session

SILKY_PYTHON_PROFILER_FUNC = my_custom_logic # profile only session has recording enabled.
```

You can also use a `lambda`.

```python
# profile only session has recording enabled.
SILKY_PYTHON_PROFILER_FUNC = lambda request: 'profile_requests' in request.session
```

### Code Generation

Silk currently generates two bits of code per request:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/9.png" width="720px"/>

Both are intended for use in replaying the request. The curl command can be used to replay via command-line and the python code can be used within a Django unit test or simply as a standalone script.

## Configuration

### Authentication/Authorisation

By default anybody can access the Silk user interface by heading to `/silk/`. To enable your Django
auth backend place the following in `settings.py`:

```python
SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions
```

If `SILKY_AUTHORISATION` is `True`, by default Silk will only authorise users with `is_staff` attribute set to `True`.

You can customise this using the following in `settings.py`:

```python
def my_custom_perms(user):
    return user.is_allowed_to_use_silk

SILKY_PERMISSIONS = my_custom_perms
```

You can also use a `lambda`.

```python
SILKY_PERMISSIONS = lambda user: user.is_superuser
```

### Request/Response bodies

By default, Silk will save down the request and response bodies for each request for future viewing
no matter how large. If Silk is used in production under heavy volume with large bodies this can have
a huge impact on space/time performance. This behaviour can be configured with the following options:

```python
SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # If response body>1024 bytes, ignore
```

### Meta-Profiling

Sometimes it is useful to be able to see what effect Silk is having on the request/response time. To do this add
the following to your `settings.py`:

```python
SILKY_META = True
```

Silk will then record how long it takes to save everything down to the database at the end of each
request:

<img src="https://raw.githubusercontent.com/jazzband/django-silk/master/screenshots/meta.png"/>

Note that in the above screenshot, this means that the request took 29ms (22ms from Django and 7ms from Silk)

### Recording a Fraction of Requests

On high-load sites it may be helpful to only record a fraction of the requests that are made. To do this add the following to your `settings.py`:

Note: This setting is mutually exclusive with SILKY_INTERCEPT_FUNC.

```python
SILKY_INTERCEPT_PERCENT = 50 # log only 50% of requests
```

#### Custom Logic for Recording Requests

On high-load sites it may also be helpful to write your own logic for when to intercept requests. To do this add the following to your `settings.py`:

Note: This setting is mutually exclusive with SILKY_INTERCEPT_PERCENT.

```python
def my_custom_logic(request):
    return 'record_requests' in request.session

SILKY_INTERCEPT_FUNC = my_custom_logic # log only session has recording enabled.
```

You can also use a `lambda`.

```python
# log only session has recording enabled.
SILKY_INTERCEPT_FUNC = lambda request: 'record_requests' in request.session
```

### Limiting request/response data

To make sure silky garbage collects old request/response data, a config var can be set to limit the number of request/response rows it stores.

```python
SILKY_MAX_RECORDED_REQUESTS = 10**4
```

The garbage collection is only run on a percentage of requests to reduce overhead.  It can be adjusted with this config:

```python
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10
```

### Enable query analysis

To enable query analysis when supported by the dbms a config var can be set in order to execute queries with the analyze features.

```python
SILKY_ANALYZE_QUERIES = True
```

### Clearing logged data

A management command will wipe out all logged data:

```bash
python manage.py silk_clear_request_log
```

## Contributing

[![Jazzband](https://jazzband.co/static/img/jazzband.svg)](https://jazzband.co/)

This is a [Jazzband](https://jazzband.co/) project. By contributing you agree to abide by the [Contributor Code of Conduct](https://jazzband.co/about/conduct) and follow the [guidelines](https://jazzband.co/about/guidelines).

### Development Environment

Silk features a project named `project` that can be used for `silk` development. It has the `silk` code symlinked so
you can work on the sample `project` and on the `silk` package at the same time.

In order to setup local development you should first install all the dependencies for the test `project`. From the
root of the `project` directory:

```bash
pip install -r requirements.txt
```

You will also need to install `silk`'s dependencies. From the root of the git repository:

```bash
pip install -e .
```

At this point your virtual environment should have everything it needs to run both the sample `project` and
`silk` successfully.

Before running, you must set the `DB_ENGINE` and `DB_NAME` environment variables:

```bash
export DB_ENGINE=sqlite3
export DB_NAME=db.sqlite3
```

For other combinations, check [`tox.ini`](./tox.ini).

Now from the root of the sample `project` apply the migrations

```bash
python manage.py migrate
```

Now from the root of the sample `project` directory start the django server

```bash
python manage.py runserver
```

#### Running the tests

```bash
cd project
./tests/test_migrations.sh
python manage.py test --noinput
```

Happy profiling!
