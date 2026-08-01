from django.conf import settings
from django.db import connections


def delete_model(model):
    engine = settings.DATABASES[model.objects.db]['ENGINE']
    table = model._meta.db_table
    if 'mysql' in engine or 'postgresql' in engine:
        # Use "TRUNCATE" on the table
        with connections[model.objects.db].cursor() as cursor:
            if 'mysql' in engine:
                cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                cursor.execute(f"TRUNCATE TABLE {table}")
                cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            elif 'postgres' in engine:
                cursor.execute(f"ALTER TABLE {table} DISABLE TRIGGER USER;")
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                cursor.execute(f"ALTER TABLE {table} ENABLE TRIGGER USER;")
        return

    # Manually delete rows because sqlite does not support TRUNCATE and
    # oracle doesn't provide good support for disabling foreign key checks
    #
    # Batch size must not exceed the database's actual query parameter
    # limit (e.g. SQLite's SQLITE_MAX_VARIABLE_NUMBER, exposed here as
    # max_query_params). This varies across SQLite builds/versions --
    # a previously hardcoded batch size that happened to work in one
    # environment could still exceed a more constrained build's real
    # limit elsewhere, causing "too many SQL variables". Capping at a
    # reasonable default (800) keeps batches efficient when the
    # backend's limit is high, while never exceeding it when the
    # limit is lower. See GH #421.
    max_query_params = connections[model.objects.db].features.max_query_params
    batch_size = min(800, max_query_params) if max_query_params else 800
    while True:
        items_to_delete = list(
            model.objects.values_list('pk', flat=True).all()[:batch_size])
        if not items_to_delete:
            break
        model.objects.filter(pk__in=items_to_delete).delete()
