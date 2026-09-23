## 1. Runtime security configuration

- [x] 1.1 Configure `CSRF_TRUSTED_ORIGINS` from the existing environment-list helper with the localhost development default, and verify the runtime-settings tests cover explicit and default values.
- [x] 1.2 Add `CSRF_TRUSTED_ORIGINS` to `.env.example` using the documented localhost value, and verify the example remains valid environment-file syntax.

## 2. Production API documentation boundaries

- [x] 2.1 Exclude the public author and post view sets from generated OpenAPI schemas in production while retaining their router registrations, and verify a production schema has no public author or post paths.
- [x] 2.2 Enable router format suffixes only in development, and verify format-suffixed routes resolve in development but not in production.

## 3. Verification

- [x] 3.1 Extend the application URL and schema tests to cover development and production behavior, and verify them with `uv run pytest project/tests/unit_test/app`.
- [x] 3.2 Run `uv run python project/manage.py check` and the relevant public API tests to verify runtime configuration and endpoint contracts remain valid.
