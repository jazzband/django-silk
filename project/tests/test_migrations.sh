#!/bin/bash
set -ev

python manage.py migrate --noinput
