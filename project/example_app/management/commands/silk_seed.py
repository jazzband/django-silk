"""
Management command: silk_seed

Populates the silk database with realistic dummy data so all UI features
can be exercised in development:

  DB_ENGINE=sqlite3 .venv/bin/python project/manage.py silk_seed
  DB_ENGINE=sqlite3 .venv/bin/python project/manage.py silk_seed --requests 300 --days 14
  DB_ENGINE=sqlite3 .venv/bin/python project/manage.py silk_seed --clear
"""

import json
import os
import random
import traceback
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from silk import models
from silk.models import Profile, SQLQuery

# ---------------------------------------------------------------------------
# Data pools
# ---------------------------------------------------------------------------

METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
METHOD_WEIGHTS = [50, 20, 10, 8, 5, 4, 3]

STATUS_CODES = [200, 201, 204, 301, 302, 400, 401, 403, 404, 422, 500, 502, 503]
STATUS_WEIGHTS = [40, 8, 4, 3, 5, 5, 3, 4, 8, 3, 8, 4, 3]

VIEW_NAMES = [
    "api:user-list",
    "api:user-detail",
    "api:product-list",
    "api:product-detail",
    "api:order-list",
    "api:order-detail",
    "api:cart-view",
    "api:checkout",
    "api:search",
    "api:auth-login",
    "api:auth-logout",
    "dashboard:index",
    "dashboard:reports",
    "dashboard:export",
    "admin:index",
    "admin:user-changelist",
    "home",
    "health-check",
]

PATHS = [
    "/api/v1/users/",
    "/api/v1/users/{id}/",
    "/api/v1/products/",
    "/api/v1/products/{id}/",
    "/api/v1/orders/",
    "/api/v1/orders/{id}/",
    "/api/v1/cart/",
    "/api/v1/checkout/",
    "/api/v1/search/?q={q}",
    "/api/v1/auth/login/",
    "/api/v1/auth/logout/",
    "/dashboard/",
    "/dashboard/reports/?period=7d",
    "/dashboard/export/?format=csv",
    "/admin/",
    "/admin/auth/user/",
    "/",
    "/health/",
]

PROFILE_NAMES = [
    "slow_serializer",
    "heavy_queryset",
    "permission_check",
    "cache_miss_handler",
    "pdf_renderer",
    "email_dispatch",
    "search_index_update",
    "data_export",
    "image_resize",
    "audit_log_write",
]

FUNC_NAMES = [
    "",
    "",
    "serialize_user",
    "build_queryset",
    "check_permissions",
    "render_template",
    "send_notification",
    "generate_report",
    "process_payment",
    "validate_input",
]

FILE_PATH = os.path.realpath(__file__)

SQL_TEMPLATES = [
    'SELECT "auth_user"."id", "auth_user"."username", "auth_user"."email" FROM "auth_user" WHERE "auth_user"."id" = %s',
    'SELECT "auth_user"."id", "auth_user"."username" FROM "auth_user" ORDER BY "auth_user"."date_joined" DESC LIMIT %s',
    'SELECT COUNT(*) AS "__count" FROM "auth_user"',
    'SELECT "app_product"."id", "app_product"."name", "app_product"."price" FROM "app_product" WHERE "app_product"."is_active" = TRUE',
    'SELECT "app_product"."id", "app_product"."name", "app_product"."price", "app_category"."name" FROM "app_product" LEFT OUTER JOIN "app_category" ON ("app_product"."category_id" = "app_category"."id") WHERE "app_product"."price" > %s ORDER BY "app_product"."name"',
    'SELECT "app_order"."id", "app_order"."status", "app_order"."total", "auth_user"."username" FROM "app_order" INNER JOIN "auth_user" ON ("app_order"."user_id" = "auth_user"."id") WHERE "app_order"."status" = %s',
    'SELECT "app_orderitem"."id", "app_orderitem"."quantity", "app_orderitem"."unit_price", "app_product"."name" FROM "app_orderitem" INNER JOIN "app_product" ON ("app_orderitem"."product_id" = "app_product"."id") WHERE "app_orderitem"."order_id" = %s',
    'INSERT INTO "app_auditlog" ("user_id", "action", "timestamp", "details") VALUES (%s, %s, %s, %s)',
    'UPDATE "app_order" SET "status" = %s, "updated_at" = %s WHERE "app_order"."id" = %s',
    'DELETE FROM "app_session" WHERE "app_session"."expire_date" < %s',
    # N+1-style query (same template executed many times per request)
    'SELECT "app_product"."id", "app_product"."name" FROM "app_product" WHERE "app_product"."id" = %s',
]

# The last SQL_TEMPLATE is the N+1 one — we'll repeat it intentionally
N1_QUERY = SQL_TEMPLATES[-1]

REQUEST_CONTENT_TYPES = ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"]
RESPONSE_CONTENT_TYPES = ["application/json", "text/html", "text/csv", "application/pdf"]

SAMPLE_JSON_BODIES = [
    '{"username": "alice", "password": "s3cr3t"}',
    '{"name": "Widget Pro", "price": 49.99, "category_id": 3}',
    '{"status": "shipped", "tracking_number": "TRK-1234567"}',
    '{"q": "blue widget", "page": 2, "per_page": 20}',
    '{"items": [{"product_id": 7, "qty": 2}, {"product_id": 12, "qty": 1}]}',
]

RESPONSE_BODIES = {
    "application/json": [
        '{"id": 42, "username": "alice", "email": "alice@example.com"}',
        '{"count": 150, "results": [{"id": 1, "name": "Widget"}, {"id": 2, "name": "Gadget"}]}',
        '{"order_id": 9981, "status": "created", "total": "149.97"}',
        '{"detail": "Not found."}',
        '{"detail": "Authentication credentials were not provided."}',
        '{"non_field_errors": ["Invalid username or password."]}',
        '{"task_id": "abc-123", "status": "queued"}',
    ],
    "text/html": ["<html><body><h1>Dashboard</h1></body></html>"],
    "text/csv": ["id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com"],
    "application/pdf": [""],
}

FAKE_CPROFILE = """\
         1234 function calls (1198 primitive calls) in 0.543 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      100    0.200    0.002    0.543    0.005 views/api.py:42(get_queryset)
      100    0.050    0.001    0.300    0.003 models.py:88(serialize)
      500    0.150    0.000    0.180    0.000 db/models/query.py:350(__iter__)
       50    0.100    0.002    0.100    0.002 serializers.py:120(validate)
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rand_time(ago_days: int, spread_days: int) -> tuple:
    """Return (start_time, end_time) at a random point within the window."""
    base = timezone.now() - timedelta(days=ago_days)
    offset = timedelta(
        seconds=random.randint(0, int(spread_days * 86400))
    )
    start_time = base + offset
    # request duration: mostly fast, occasionally slow
    weights = [60, 25, 10, 4, 1]
    bucket = random.choices([50, 300, 800, 2000, 5000], weights=weights)[0]
    duration_ms = random.randint(max(1, bucket - 50), bucket + 200)
    end_time = start_time + timedelta(milliseconds=duration_ms)
    return start_time, end_time


def _resolve_path(path_template: str) -> str:
    return (
        path_template
        .replace("{id}", str(random.randint(1, 9999)))
        .replace("{q}", random.choice(["widget", "gadget", "blue+thing", "sale"]))
    )


def _make_sql(request=None, profile=None, n=1, force_query=None) -> list:
    """Create n SQLQuery objects, optionally bound to request/profile."""
    now = timezone.now()
    queries = []
    for _ in range(n):
        duration_ms = random.randint(1, 150)
        start = now - timedelta(milliseconds=random.randint(0, 5000))
        end = start + timedelta(milliseconds=duration_ms)
        tb = "".join(reversed(traceback.format_stack()))
        q = SQLQuery.objects.create(
            query=force_query or random.choice(SQL_TEMPLATES[:-1]),
            start_time=start,
            end_time=end,
            time_taken=duration_ms,
            request=request,
            traceback=tb,
        )
        queries.append(q)
    if profile:
        profile.queries.set(queries)
    return queries


def _make_profile(request=None) -> Profile:
    start_time, end_time = _rand_time(
        ago_days=random.randint(0, 6), spread_days=1
    )
    dynamic = random.choice([True, False])
    p = Profile.objects.create(
        start_time=start_time,
        end_time=end_time,
        time_taken=(end_time - start_time).total_seconds() * 1000,
        request=request,
        name=random.choice(PROFILE_NAMES),
        file_path=FILE_PATH,
        line_num=random.randint(1, 50),
        func_name=random.choice(FUNC_NAMES),
        dynamic=dynamic,
        end_line_num=random.randint(51, 100) if dynamic else None,
        exception_raised=random.random() < 0.05,
    )
    _make_sql(request=request, profile=p, n=random.randint(0, 8))
    return p


# ---------------------------------------------------------------------------
# Scenario builders
# ---------------------------------------------------------------------------

def _make_normal_request(ago_days: int, spread_days: int) -> models.Request:
    start_time, end_time = _rand_time(ago_days, spread_days)
    time_taken = (end_time - start_time).total_seconds() * 1000
    num_sql = random.randint(0, 15)
    method = random.choices(METHODS, weights=METHOD_WEIGHTS)[0]
    path_tmpl, view = random.choice(list(zip(PATHS, VIEW_NAMES)))
    path = _resolve_path(path_tmpl)
    req_ct = random.choice(REQUEST_CONTENT_TYPES)
    req_body = random.choice(SAMPLE_JSON_BODIES) if req_ct == "application/json" else ""

    request = models.Request.objects.create(
        method=method,
        path=path,
        query_params=json.dumps({"page": str(random.randint(1, 5))}) if "?" not in path else "{}",
        num_sql_queries=num_sql,
        start_time=start_time,
        end_time=end_time,
        time_taken=time_taken,
        view_name=view,
        encoded_headers=json.dumps({"content-type": req_ct, "accept": "application/json"}),
        body=req_body,
        meta_time=round(random.uniform(0.5, 5.0), 3),
        meta_time_spent_queries=round(random.uniform(0.0, time_taken * 0.8), 3),
    )

    res_ct = random.choice(RESPONSE_CONTENT_TYPES)
    res_body = random.choice(RESPONSE_BODIES[res_ct])
    models.Response.objects.create(
        request=request,
        status_code=random.choices(STATUS_CODES, weights=STATUS_WEIGHTS)[0],
        encoded_headers=json.dumps({"content-type": res_ct}),
        body=res_body,
    )

    _make_sql(request=request, n=num_sql)

    for _ in range(random.randint(0, 2)):
        _make_profile(request=request)

    return request


def _make_n1_request(ago_days: int, spread_days: int) -> models.Request:
    """A request that triggers N+1 detection (same query repeated 15 times)."""
    start_time, end_time = _rand_time(ago_days, spread_days)
    # Make it slow due to N+1
    end_time = start_time + timedelta(milliseconds=random.randint(800, 2500))
    n1_count = random.randint(15, 30)
    time_taken = (end_time - start_time).total_seconds() * 1000
    path = _resolve_path("/api/v1/orders/{id}/")

    request = models.Request.objects.create(
        method="GET",
        path=path,
        query_params="{}",
        num_sql_queries=n1_count + random.randint(1, 3),
        start_time=start_time,
        end_time=end_time,
        time_taken=time_taken,
        view_name="api:order-detail",
        encoded_headers=json.dumps({"content-type": "application/json"}),
        body="",
        meta_time=round(random.uniform(1.0, 8.0), 3),
        meta_time_spent_queries=round(time_taken * 0.7, 3),
    )

    models.Response.objects.create(
        request=request,
        status_code=200,
        encoded_headers=json.dumps({"content-type": "application/json"}),
        body='{"id": 9981, "items": [...]}',
    )

    # The repeated N+1 query
    _make_sql(request=request, n=n1_count, force_query=N1_QUERY)
    # A few normal queries too
    _make_sql(request=request, n=random.randint(1, 3))

    return request


def _make_error_request(ago_days: int, spread_days: int) -> models.Request:
    """500 / 4xx requests."""
    start_time, end_time = _rand_time(ago_days, spread_days)
    time_taken = (end_time - start_time).total_seconds() * 1000
    path = _resolve_path(random.choice(["/api/v1/users/{id}/", "/api/v1/products/{id}/"]))
    status = random.choice([400, 401, 403, 404, 500])

    request = models.Request.objects.create(
        method=random.choice(["GET", "POST", "DELETE"]),
        path=path,
        query_params="{}",
        num_sql_queries=random.randint(0, 5),
        start_time=start_time,
        end_time=end_time,
        time_taken=time_taken,
        view_name=random.choice(VIEW_NAMES),
        encoded_headers=json.dumps({"content-type": "application/json"}),
        body="",
        meta_time=round(random.uniform(0.1, 2.0), 3),
        meta_time_spent_queries=0.0,
    )

    error_body = (
        '{"detail": "Not found."}' if status == 404
        else '{"detail": "Internal server error."}' if status == 500
        else '{"detail": "Permission denied."}'
    )
    models.Response.objects.create(
        request=request,
        status_code=status,
        encoded_headers=json.dumps({"content-type": "application/json"}),
        body=error_body,
    )

    _make_sql(request=request, n=request.num_sql_queries)
    return request


def _make_slow_request(ago_days: int, spread_days: int) -> models.Request:
    """Very slow request with cProfile data."""
    start_time = timezone.now() - timedelta(
        days=ago_days, seconds=random.randint(0, int(spread_days * 86400))
    )
    duration_ms = random.randint(3000, 10000)
    end_time = start_time + timedelta(milliseconds=duration_ms)
    num_sql = random.randint(20, 60)

    request = models.Request.objects.create(
        method="GET",
        path="/dashboard/reports/?period=7d",
        query_params='{"period": "7d", "format": "json"}',
        num_sql_queries=num_sql,
        start_time=start_time,
        end_time=end_time,
        time_taken=duration_ms,
        view_name="dashboard:reports",
        encoded_headers=json.dumps({"content-type": "application/json"}),
        body="",
        meta_time=round(random.uniform(5.0, 20.0), 3),
        meta_time_spent_queries=round(duration_ms * 0.85, 3),
        pyprofile=FAKE_CPROFILE,
    )

    models.Response.objects.create(
        request=request,
        status_code=200,
        encoded_headers=json.dumps({"content-type": "application/json"}),
        body='{"rows": 1500, "generated_at": "2024-01-15T12:00:00Z"}',
    )

    _make_sql(request=request, n=num_sql)

    for _ in range(random.randint(2, 5)):
        _make_profile(request=request)

    return request


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Seed the silk database with realistic dummy data for UI development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--requests",
            type=int,
            default=200,
            help="Total number of requests to create (default: 200)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Spread requests over this many past days (default: 7)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing silk data before seeding",
        )

    def handle(self, *args, **options):
        n_requests = options["requests"]
        days = options["days"]

        if options["clear"]:
            self.stdout.write("Clearing existing silk data…")
            Profile.objects.all().delete()
            SQLQuery.objects.all().delete()
            models.Response.objects.all().delete()
            models.Request.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("  Cleared."))

        self.stdout.write(f"Seeding {n_requests} requests spread over {days} days…")

        # Scenario mix (percentages)
        n_normal = int(n_requests * 0.70)
        n_n1 = int(n_requests * 0.10)
        n_error = int(n_requests * 0.12)
        n_slow = n_requests - n_normal - n_n1 - n_error  # remainder (~8%)

        created = 0

        for i in range(n_normal):
            ago = random.randint(0, days - 1)
            _make_normal_request(ago_days=ago, spread_days=1)
            created += 1
            if created % 50 == 0:
                self.stdout.write(f"  …{created}/{n_requests}")

        for i in range(n_n1):
            ago = random.randint(0, days - 1)
            _make_n1_request(ago_days=ago, spread_days=1)
            created += 1

        for i in range(n_error):
            ago = random.randint(0, days - 1)
            _make_error_request(ago_days=ago, spread_days=1)
            created += 1

        for i in range(n_slow):
            ago = random.randint(0, days - 1)
            _make_slow_request(ago_days=ago, spread_days=1)
            created += 1

        # Summary
        req_count = models.Request.objects.count()
        sql_count = SQLQuery.objects.count()
        prof_count = Profile.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {created} requests.\n"
                f"  Total requests in DB : {req_count}\n"
                f"  Total SQL queries    : {sql_count}\n"
                f"  Total profiles       : {prof_count}\n"
                f"\nFeatures exercised:\n"
                f"  ✓ Multi-method requests (GET/POST/PUT/PATCH/DELETE)\n"
                f"  ✓ Various status codes (2xx / 3xx / 4xx / 5xx)\n"
                f"  ✓ N+1 detection (repeated queries per request)\n"
                f"  ✓ Slow requests with cProfile data\n"
                f"  ✓ SQL query list + detail views\n"
                f"  ✓ Profile list + detail views\n"
                f"  ✓ Time-range distribution for timeline chart\n"
                f"  ✓ Multiple view names for top-N tables\n"
            )
        )
