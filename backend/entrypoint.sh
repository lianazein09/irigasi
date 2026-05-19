#!/bin/sh
set -eu

DB_ENGINE_NORMALIZED=$(printf '%s' "${DB_ENGINE:-mysql}" | tr '[:upper:]' '[:lower:]')

if [ "$DB_ENGINE_NORMALIZED" = "postgres" ] || [ "$DB_ENGINE_NORMALIZED" = "postgresql" ]; then
  python /app/ensure_postgres_schema.py
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"
