## Context

See `proposal.md` for motivation. The repository declares Python 3.14 and its dependencies through `pyproject.toml` and `uv.lock`; Django currently serves locally with a SQLite database under `project/`. `ALLOWED_HOSTS` has local defaults but is already environment-driven, so the implementation can extend that configuration without changing the application routes.

## Goals / Non-Goals

**Goals:**

- Provide a single Docker Compose entry point for a reproducible WSGI application server.
- Keep the source tree shared bidirectionally while isolating `.venv` in Docker-managed storage.
- Permit explicitly configured external host headers while preserving local development defaults.

**Non-Goals:**

- Production hardening beyond the configured WSGI process, TLS termination, or deployment orchestration.
- Replacing SQLite with a networked database or adding infrastructure services.
- Sharing the container's virtual environment with the host or supporting host-managed dependency installation.

## Decisions

### Alpine-based development image

Use an Alpine Python 3.14 image and install Git plus uv in the image. This satisfies the requested lightweight base and makes the required tooling independent of the host. A Debian-based Python image was considered for broader prebuilt binary compatibility, but it does not meet the Alpine requirement.

### Bind mount source and mask `.venv` with a named volume

Mount the repository at the container work directory for immediate bidirectional edits. Overlay its `.venv` path with a named Docker volume and configure uv to use that location, so dependency state persists across container recreation but never appears in the host checkout. Copying source into the image alone was rejected because it requires rebuilding for each edit; mounting the complete repository alone was rejected because it would expose the virtual environment to the host.

### Compose-managed WSGI command

The Compose service will synchronize the locked dependencies, run required database migrations, and launch Gunicorn against `app.wsgi:application` from the `project/` directory. Gunicorn will bind to `0.0.0.0:8000`, which Compose publishes to the host. Django's development server was rejected because the requested runtime is WSGI rather than the autoreloading development process.

### Explicit runtime configuration

Use environment variables for `SECRET_KEY`, `DEBUG`, `ENVIRONMENT`, `ALLOWED_HOSTS`, and `API_BASE_URL`. Compose will load caller-provided values while supplying development-safe defaults for non-secret settings. SQLite remains the default database and its file stays in the bind-mounted project directory. Hard-coding `*` for `ALLOWED_HOSTS` was rejected because it weakens Django host-header validation.

## Risks / Trade-offs

- [Alpine packages or Python dependencies may need compilation support] → Install only the required runtime and build packages, and document how to rebuild after dependency changes.
- [Named volume dependencies can become stale after lockfile changes] → Run `uv sync` when the service starts so the environment reconciles with the lockfile.
- [Gunicorn does not automatically reload source files] → Enable its development reload mode so bind-mounted source edits restart workers.
- [Publishing the port makes the development server reachable beyond the host when Docker permits it] → Require explicit `ALLOWED_HOSTS` values for non-local access and document that this environment is development-only.

## Migration Plan

1. Add the Docker image, Compose configuration, and Docker build exclusions.
2. Update the host configuration and add tests for default and configured permitted hosts.
3. Start the service with Docker Compose and verify the Gunicorn-served admin and API routes through the published port.
4. Roll back by stopping and removing the Compose service and named virtual-environment volume; existing local `uv` workflows and SQLite data remain usable.
