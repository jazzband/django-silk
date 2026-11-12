Profiling
=========

Silk can be used to profile arbitrary blocks of code and provides ``silk_profile``, a Python decorator and a context manager for this purpose. Profiles will then appear in the 'Profiling' tab within Silk's user interface.

Decorator
---------

The decorator can be applied to both functions and methods:

.. code-block:: python

	@silk_profile(name='View Blog Post')
	def post(request, post_id):
	    p = Post.objects.get(pk=post_id)
	    return render(request, 'post.html', {
	        'post': p
	    })


.. code-block:: python

	class MyView(View):    
		@silk_profile(name='View Blog Post')
		def get(self, request):
			p = Post.objects.get(pk=post_id)
	    	return render(request, 'post.html', {
	        	'post': p
	    	})

Context Manager
---------------

``silk_profile`` can also be used as a context manager:

.. code-block:: python

	def post(request, post_id):
	    with silk_profile(name='View Blog Post #%d' % self.pk):
	        p = Post.objects.get(pk=post_id)
	    	return render(request, 'post.html', {
	        	'post': p
	    	})

Dynamic Profiling
-----------------

Decorators and context managers can also be injected at run-time. This is useful if we want to narrow down slow requests/database queries to dependencies.

Dynamic profiling is configured via the ``SILKY_DYNAMIC_PROFILING`` option in your ``settings.py``:

.. code-block:: python

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
	class MyClass:

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

	"""
	Dynamic wildcard decorators
	"""

	SILKY_DYNAMIC_PROFILING = [
	    # every function defined in path.to.module
	    {'module': 'path.to.module', 'function': '*'},
	    # every method of MyClass
	    {'module': 'path.to.module', 'function': 'MyClass.*'},
	    # every method starting with ``get_`` of the classes ending with ``View``
	    {'module': 'path.to.module', 'function': '*View.get_*'},
	]

Wildcards follow the rules of Python's :mod:`fnmatch` (``*``, ``?`` and ``[seq]``). The pattern is
matched against plain functions defined in the module itself, or, for ``Class.method`` patterns,
against the classes defined in the module and their methods. Imported objects, static/class methods
and dunder methods (e.g. ``__init__``, unless the pattern starts with ``__``) are not matched. A
pattern that matches nothing raises an ``AttributeError``, and wildcards cannot be combined with
``start_line``/``end_line``. If ``name`` is given it is used for every matched function, otherwise each
function's own name is used.

Note that dynamic profiling behaves in a similar fashion to that of the python mock framework in that
we modify the function in-place e.g:

.. code-block:: python

	""" my.module """
	from another.module import foo

	# ...do some stuff
	foo()
	# ...do some other stuff


We would profile ``foo`` by dynamically decorating `my.module.foo` as opposed to ``another.module.foo``:

.. code-block:: python

	SILKY_DYNAMIC_PROFILING = [{
	    'module': 'my.module',
	    'function': 'foo'
	}]

If we were to apply the dynamic profile to the functions source module ``another.module.foo`` *after* it has already been imported, no profiling would be triggered.
