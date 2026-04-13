# django-silk

[![PyPI](https://img.shields.io/pypi/v/django-silk.svg)](https://pypi.org/project/django-silk/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-silk.svg)](https://pypi.org/project/django-silk/)
[![Supported Django versions](https://img.shields.io/pypi/djversions/django-silk.svg)](https://pypi.org/project/django-silk/)
[![Tests](https://github.com/jazzband/django-silk/actions/workflows/test.yml/badge.svg)](https://github.com/jazzband/django-silk/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**django-silk** is a live profiling and inspection tool for the Django framework.

Silk intercepts and stores HTTP requests and database queries made during those requests, presenting them in a browsable web UI with filtering, sorting, and code profiling capabilities.

---

## Requirements

* Django 4.2, 5.1, 5.2, 6.0
* Python 3.10, 3.11, 3.12, 3.13, 3.14

---

## Installation

```bash
pip install django-silk
```

With optional request body formatting:

```bash
pip install django-silk[formatting]
```

### settings.py

```python
MIDDLEWARE = [
    ...
    'silk.middleware.SilkyMiddleware',
    ...
]

TEMPLATES = [{
    ...
    'OPTIONS': {
        'context_processors': [
            ...
            'django.template.context_processors.request',
        ],
    },
}]

INSTALLED_APPS = [
    ...
    'silk',
]
```

> **Middleware order:** Any middleware placed *before* `SilkyMiddleware` that returns a response without calling `get_response` will prevent Silk from running. If you use `django.middleware.gzip.GZipMiddleware`, place it **before** `SilkyMiddleware`.

### urls.py

```python
from django.urls import include, path

urlpatterns += [
    path('silk/', include('silk.urls', namespace='silk')),
]
```

### Migrate and collect static

```bash
python manage.py migrate
python manage.py collectstatic
```

The UI is now available at `/silk/`.

---

## Features

### Request Inspection

Silk's middleware records every HTTP request and response — method, status code, path, timing, SQL query count, and headers/bodies — and presents them in a filterable, sortable, paginated table.

### SQL Inspection

Every SQL query executed during a request is captured with its execution time, tables involved, number of joins, and a full stack trace so you can see exactly where in your code it was triggered.

### Code Profiling

#### Decorator / context manager

```python
from silk.profiling.profiler import silk_profile

@silk_profile(name='View Blog Post')
def post(request, post_id):
    p = Post.objects.get(pk=post_id)
    return render(request, 'post.html', {'post': p})
```

```python
def post(request, post_id):
    with silk_profile(name='View Blog Post #%d' % post_id):
        p = Post.objects.get(pk=post_id)
        return render(request, 'post.html', {'post': p})
```

#### cProfile integration

```python
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True  # also save .prof files
```

When enabled, a call-graph coloured by time is shown on the profile detail page.

#### Dynamic profiling

Profile third-party code without touching its source:

```python
SILKY_DYNAMIC_PROFILING = [{
    'module': 'path.to.module',
    'function': 'MyClass.bar',
}]
```

### Code Generation

Silk generates a `curl` command and a Django test-client snippet for every request, making it easy to replay a captured request from the terminal or a unit test.

---

## Configuration

### Authentication

```python
SILKY_AUTHENTICATION = True   # user must be logged in
SILKY_AUTHORISATION = True    # user must have is_staff=True (default)

# Custom permission check:
SILKY_PERMISSIONS = lambda user: user.is_superuser
```

### Request / response body limits

```python
SILKY_MAX_REQUEST_BODY_SIZE = -1    # -1 = no limit
SILKY_MAX_RESPONSE_BODY_SIZE = 1024 # bytes; larger bodies are discarded
```

### Sampling (high-traffic sites)

```python
SILKY_INTERCEPT_PERCENT = 50  # record only 50 % of requests
# or
SILKY_INTERCEPT_FUNC = lambda request: 'profile' in request.session
```

### Garbage collection

```python
SILKY_MAX_RECORDED_REQUESTS = 10_000
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10  # GC runs on 10 % of requests
```

Trigger manually (e.g. from a cron job):

```bash
python manage.py silk_request_garbage_collect
```

Clear all data immediately:

```bash
python manage.py silk_clear_request_log
```

### Query analysis

```python
SILKY_ANALYZE_QUERIES = True
SILKY_EXPLAIN_FLAGS = {'format': 'JSON', 'costs': True}
```

> **Warning:** `EXPLAIN ANALYZE` on PostgreSQL actually executes the query, which may cause unintended side effects. Use with caution.

### Meta-profiling

```python
SILKY_META = True  # shows how long Silk itself takes per request
```

### Sensitive data masking

```python
# Default set — case insensitive
SILKY_SENSITIVE_KEYS = {'username', 'api', 'token', 'key', 'secret', 'password', 'signature'}
```

### Custom profiler storage

```python
# Django >= 4.2
STORAGES = {
    'SILKY_STORAGE': {
        'BACKEND': 'path.to.StorageClass',
    },
}

SILKY_PYTHON_PROFILER_RESULT_PATH = '/path/to/profiles/'
```

---

## Development

```bash
git clone https://github.com/jazzband/django-silk.git
cd django-silk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[formatting]"
pip install -r project/requirements.txt

# Run the example project
DB_ENGINE=sqlite3 python project/manage.py migrate
DB_ENGINE=sqlite3 python project/manage.py runserver
# Visit http://127.0.0.1:8000/silk/  (login: admin / admin)

# Watch SCSS while editing UI
npx gulp watch

# Run tests
DB_ENGINE=sqlite3 python -m pytest project/tests/ -q
```

---

## License

MIT — see [LICENSE](LICENSE).
