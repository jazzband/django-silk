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
