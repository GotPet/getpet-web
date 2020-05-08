#!/bin/bash
set -e

echo "==> Django setup, executing: collectstatic"
python manage.py collectstatic --noinput

echo "==> Django setup, executing: migrate"
python manage.py migrate

echo "==> Starting uWSGI ..."
gunicorn getpet.wsgi --bind 0.0.0.0:8080 --workers 5