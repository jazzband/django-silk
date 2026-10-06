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
    while True:
        items_to_delete = list(
            model.objects.values_list('pk', flat=True).all()[:800])
        if not items_to_delete:
            break
        model.objects.filter(pk__in=items_to_delete).delete()


def clear_silk_data():
    """Delete silk request logs, preserving in-flight requests.

    In-flight requests have ``end_time`` unset. Clearing them races with
    response finalization and can raise IntegrityError when silk inserts a
    Response for a Request that was just deleted.
    """
    # Imported lazily to avoid circular imports at module load.
    from silk.models import Profile, Request, Response, SQLQuery

    in_flight_ids = list(
        Request.objects.filter(end_time__isnull=True).values_list('pk', flat=True)
    )
    if not in_flight_ids:
        delete_model(Profile)
        delete_model(SQLQuery)
        delete_model(Response)
        delete_model(Request)
        return

    Profile.objects.exclude(request_id__in=in_flight_ids).delete()
    SQLQuery.objects.exclude(request_id__in=in_flight_ids).delete()
    Response.objects.exclude(request_id__in=in_flight_ids).delete()
    Request.objects.exclude(pk__in=in_flight_ids).delete()
