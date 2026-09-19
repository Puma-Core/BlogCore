#!/bin/sh

set -eu

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

uv sync --frozen
uv run python project/manage.py migrate
uv run python project/manage.py collectstatic --noinput

if [ "$ENVIRONMENT" = "development" ]; then
    exec uv run gunicorn --reload --chdir project --bind "0.0.0.0:${DJANGO_PORT}" app.wsgi:application
fi

exec uv run gunicorn --chdir project --bind "0.0.0.0:${DJANGO_PORT}" app.wsgi:application
