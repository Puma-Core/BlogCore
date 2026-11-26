## 1. Database Configuration

- [x] 1.1 Add the PostgreSQL driver dependency and refresh `uv.lock`; verify a clean `uv sync` installs the driver on Python 3.14.
- [x] 1.2 Convert the current `project/app/settings.py` module into a settings package and add `project/app/settings/database.py`; verify Django entry points continue loading the settings package.
- [x] 1.3 Extract backend selection and database environment-variable parsing into `settings/database.py`, retaining SQLite as the default and failing visibly when PostgreSQL is selected with incomplete configuration.
- [x] 1.4 Add unit tests for SQLite defaults, custom PostgreSQL connection values, explicit SQLite selection, and incomplete PostgreSQL configuration errors without a silent SQLite fallback.

## 2. Container Runtime

- [x] 2.1 Update the Django Compose service to pass PostgreSQL connection variables for an external instance; verify Compose contains no PostgreSQL service, volume, healthcheck, or `depends_on` entry.
- [x] 2.2 Add a retryable startup path for the Django service when the external PostgreSQL backend is selected; verify statically that Compose renders the configured external variables while an unconfigured local run remains on SQLite. Docker-specific `docker compose config` validation is deferred to a Docker-capable environment.
- [ ] 2.3 Start Django with an externally managed PostgreSQL instance, run Django migrations, and verify the admin/API process can execute a database query without Compose provisioning PostgreSQL. (Blocked locally: no external PostgreSQL instance is configured.)

## 3. Data Migration And Documentation

- [x] 3.1 Document PostgreSQL environment variables, external instance prerequisites, local startup, connection inspection, and the fact that database lifecycle is managed outside Compose.
- [x] 3.2 Document the selected backend behavior, required PostgreSQL variables, visible configuration errors, and the fact that this change does not transfer existing data.
- [x] 3.3 Update the project configuration documentation and examples so SQLite remains the implicit default and PostgreSQL variables are documented as an explicit override.

## 4. Validation

- [x] 4.1 Run `uv run python project/manage.py check` with PostgreSQL configuration and the focused settings tests.
- [x] 4.2 Run the full test suite and validate the startup script syntax; verify statically that Compose has no PostgreSQL service. Running `docker compose config` and `docker compose up --build` is optional and deferred to a Docker-capable environment.
