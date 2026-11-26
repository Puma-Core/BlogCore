FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_PORT=8000

RUN apk add --no-cache git \
    && pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project

COPY docker/start.sh /usr/local/bin/start
RUN chmod +x /usr/local/bin/start

ENTRYPOINT ["/usr/local/bin/start"]
