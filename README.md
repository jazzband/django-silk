silky
=====

[![Build Status](https://travis-ci.org/mtford90/silky.svg?branch=master)](https://travis-ci.org/mtford90/silky)

A silky smooth profiling and inspection tool for the Django framework. Tested with:

* Django: 1.5, 1.6
* Python: 2.7, 3.3, 3.4

## Features

### Request Inspection

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/request.png)

### SQL Inspection

SQL queries can be inspected on a per profile or per request basis:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/sql_list.png)

We can inspect the query itself:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/sql.png)

And we can also trace it to its origins:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/stack_trace.png)


### Profiling 

#### Decorator/Context Manager

As a decorator to a function or method:
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

We could also use a context manager to refine the name:

```
def post(request, post_id):
    with silk_profile(name='View Blog Post #%d' % self.pk):
        p = Post.objects.get(pk=post_id)
    	return render_to_response('post.html', {
        	'post': p
    	})
```

#### Dynamic Profiling

In situations where we have read-only access to dependencies we can dynamically profile 
code at runtime through the use of `settings.py`. The below demonstrates the possiblities:

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

Note that dynamic profiling behaves in a similar fashion to that of the python mock framework. e.g. 
given that we have the code:

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

### Code Generation

Silk features code generation that allows for replaying of intercepted requests. For example if we intercept a call to my blogs admin interface:

![profile](https://raw.githubusercontent.com/mtford90/silky/master/screenshots/admin.png)

...with a body of `cmd-1=publish&cmd-%2Fdev%2Fsilk.md=process`

This can be written as a curl command:

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
