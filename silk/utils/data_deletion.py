from django.conf import settings
from django.db import connection


def delete_model(model):
    engine = settings.DATABASES[model.objects.db]['ENGINE']
    table = model._meta.db_table
    if 'mysql' in engine or 'postgresql' in engine:
        # Use "TRUNCATE" on the table
        with connection.cursor() as cursor:
            if 'mysql' in engine:
                cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
                cursor.execute("TRUNCATE TABLE {0}".format(table))
                cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            elif 'postgres' in engine:
                cursor.execute("ALTER TABLE {0} DISABLE TRIGGER USER;".format(table))
                cursor.execute("TRUNCATE TABLE {0} CASCADE".format(table))
                cursor.execute("ALTER TABLE {0} ENABLE TRIGGER USER;".format(table))
        return

    # Manually delete rows because sqlite does not support TRUNCATE and
    # oracle doesn't provide good support for disabling foreign key checks
    while True:
        items_to_delete = list(
            model.objects.values_list('pk', flat=True).all()[:1000])
        if not items_to_delete:
            break
        model.objects.filter(pk__in=items_to_delete).delete()
