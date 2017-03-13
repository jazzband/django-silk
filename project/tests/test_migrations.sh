#!/bin/bash
set -ev

# Use migrate for Django>=1.6.0,<1.7.0
if (pip freeze | grep Django==1.[6-7].[0-9]*)
then
  python django-admin.py syncdb --noinput
fi

# Use migrate for Django>=1.8.0,<1.10.0
if (pip freeze | grep Django==1.[8-9\|10].[0-9]*)
then
  python manage.py migrate --noinput
fi
