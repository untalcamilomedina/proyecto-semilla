#!/usr/bin/env bash
set -euo pipefail

export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "Running Django deploy checks..."
python manage.py check --deploy

echo "Running migrations (public + tenants)..."
python manage.py migrate_tenants --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Deploy smoke OK"

