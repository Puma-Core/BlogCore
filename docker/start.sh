#!/bin/sh

set -eu

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

uv sync --frozen

if [ "${DATABASE_ENGINE:-sqlite}" = "postgres" ] || [ "${DATABASE_ENGINE:-sqlite}" = "postgresql" ]; then
    PYTHONPATH=project uv run python -c "from app.settings.database import DATABASES"

    attempts=0
    until uv run python project/manage.py migrate; do
        attempts=$((attempts + 1))
        if [ "$attempts" -ge 30 ]; then
            echo "PostgreSQL did not become available after 30 attempts" >&2
            exit 1
        fi
        sleep 2
    done
else
    uv run python project/manage.py migrate
fi

uv run python project/manage.py collectstatic --noinput

if [ "$ENVIRONMENT" = "development" ]; then
    exec uv run gunicorn --reload --chdir project --bind "0.0.0.0:${DJANGO_PORT}" app.wsgi:application
fi

exec uv run gunicorn --chdir project --bind "0.0.0.0:${DJANGO_PORT}" app.wsgi:application
