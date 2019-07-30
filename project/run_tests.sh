#!/bin/sh
set -ev

cd "$(dirname "$0")"
python manage.py migrate --noinput
python manage.py test --noinput
