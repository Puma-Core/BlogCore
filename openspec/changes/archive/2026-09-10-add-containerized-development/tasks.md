## 1. Container Environment

- [x] 1.1 Add an Alpine-based Dockerfile that installs Python 3.14, Git, and uv, and verify `docker compose build` completes without host Python or uv.
- [x] 1.2 Add Docker build exclusions that omit local virtual environments, caches, and repository metadata not needed to build the image, and verify the build context excludes `.venv`.
- [x] 1.3 Add a Docker Compose development service that bind-mounts the repository and overlays `.venv` with a named Docker volume, and verify source edits made from both host and container are visible to the other.
- [x] 1.4 Add the WSGI server dependency and configure startup to synchronize locked dependencies, apply migrations, and serve `app.wsgi:application` on `0.0.0.0:8000`, and verify `docker compose up` leaves the WSGI process running.

## 2. External HTTP Configuration

- [x] 2.1 Update Django runtime configuration to read secret key, debug mode, environment name, API base URL, and permitted hosts from environment variables while retaining SQLite, and verify focused settings tests cover default and configured values.
- [x] 2.2 Publish the Django HTTP port through Docker Compose and inject the runtime environment variables into the WSGI service, and verify `/admin/` and a documented API endpoint respond through the published port.

## 3. Documentation And Validation

- [x] 3.1 Document Docker Compose startup, WSGI runtime variables, common development commands, and teardown, and verify the documented startup command runs from a clean checkout with only Docker installed.
- [x] 3.2 Run `uv run python project/manage.py check`, the relevant pytest tests, and `docker compose config`, and verify all commands succeed.
