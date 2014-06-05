silky
=====

[![Build Status](https://travis-ci.org/mtford90/silky.svg?branch=master)](https://travis-ci.org/mtford90/silky)

A silky smooth profiling and inspection tool for the Django framework. Tested with:

* Django: 1.5, 1.6
* Python: 2.7, 3.3, 3.4

* [Roadmap](#Roadmap)

<a name='Features'/>
## Features

### Request Inspection

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/request.png)

The Silk middleware intercepts requests and stores associated data for later inspection. Through
the silk UI we can view:

* Time taken
* Num. queries
* Time spent on queries
* Request/Response headers
* Request/Response bodies

### SQL Inspection

SQL queries are also intercepted on a per profile/per request basis:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/sql_list.png)

We can inspect the query itself:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/sql.png)

And we can also trace it to its origins:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/stack_trace.png)


### Profiling 

Silk can be used to profile arbitrary blocks of code/functions using Python decorators and context managers. The 
profiler will record:

* Time taken 
* Time spent in database
* Number of queries

These properties can then be viewed from the Silk interface. Like with requests, we can also inspect
the SQL queries themselves as well as view the stack trace.

It is also possible to view the results of Profiling on a per-request basis.

#### Decorator

The silk decorator can be applied to both functions and methods

```python
@silk_profile(name='View Blog Post')
def post(request, post_id):
    p = Post.objects.get(pk=post_id)
    return render_to_response('post.html', {
        'post': p
    })

class MyView(View):    
	@silk_profile(name='View Blog Post')
	def get(self, request):
		p = Post.objects.get(pk=post_id)
    	return render_to_response('post.html', {
        	'post': p
    	})
```

Which would provide us with the following:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/profile.png)

#### Context Manager

Using a context manager means we can add additional context to the name which can be useful for 
narrowing down slowness to particular database records.

```
def post(request, post_id):
    with silk_profile(name='View Blog Post #%d' % self.pk):
        p = Post.objects.get(pk=post_id)
    	return render_to_response('post.html', {
        	'post': p
    	})
```

#### Dynamic Profiling

In some situations we do not have write-access to code that we depend on, such as system-level python libraries. The `SILKY_DYNAMIC_PROFILING` option of `settings.py` allows us to specify areas
of code that should be profiled without modification of the source files themselves. This is useful
for narrowing down slow pieces of code in external dependencies. 

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

### Code Generation

Silk features code generation that allows for replaying of intercepted requests. For example if we intercept a call to my blogs admin interface:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/admin.png)

...with a body of `cmd-1=publish&cmd-%2Fdev%2Fsilk.md=process`

This can be written as the curl command:

```
curl -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d 'cmd-1=&cmd-%2Fdev%2Fsilk.md=process' http://localhost:8002/admin/
```

and also through use of the Django test client which can then be used for replay/testing:

```
from django.test import Client
c = Client()
response = c.post(path='/admin/',
                  data='cmd-1=&cmd-%2Fdev%2Fsilk.md=process',
                  content_type='application/x-www-form-urlencoded')
```

## Installation

### Existing Release

Release of Silk are [here](https://github.com/mtford90/silk/releases)

Once downloaded, run:

```bash
pip install dist/django-silk-<version>.tar.gz
```

Then configure Silk in `settings.py`:

```python
MIDDLEWARE_CLASSES = (
    ...
    'silk.middleware.SilkyMiddleware',
)

INSTALLED_APPS = (
    ...
    'silk'
)
```

and to your `urls.py`:

```python
urlpatterns += patterns'('', url(r'^silk', include('silk.urls', namespace='silk')),
```

before running syncdb:

```python
python manage.py syncdb
```

Silk will automatically begin interception of requests and you can proceed to add profiling
if required. The UI can be reached at `/silk/`

### Master

First download the [source](https://github.com/mtford90/silky/archive/master.zip), unzip and
navigate via the terminal to the source directory. Then run:

```bash
python package.py mas
```

You can either install via pip:

```bash
pip install dist/django-silk-mas.tar.gz
```

or run setup.py:

```bash
tar -xvf dist/django-silk-mas.tar.gz
python dist/django-silk-mas/setup.py
```

You can then follow the steps in 'Existing Release' to include Silk in your Django project.

## Roadmap

I would eventually like to use this in a production environment. There are a number of things preventing that right now:

* Questionable stability.
    * Occasional request failures caused by Silk. (TODO: Issues)
* Effect on performance.
    * For every SQL query executed, Silk executes another query
* Space concerns.
    * Silk would quickly generate a huge number of database records.
    * Silk saves down both the request body and response body for each and every request handled by Django.
* Security risks involved in making the Silk UI available.
    * e.g. POST of password forms
    * exposure of session cookies
