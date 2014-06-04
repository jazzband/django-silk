def delete_all_models(model_class):
    """
    A sqlite3-safe deletion function to avoid "django.db.utils.OperationalError: too many SQL variables"

    :param model_class:
    :return:
    """
    while model_class.objects.count():
            ids = model_class.objects.values_list('pk', flat=True)[:100]
            model_class.objects.filter(pk__in = ids).delete()