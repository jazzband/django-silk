import django
setup = getattr(django, 'setup', None)
if setup:
    setup()