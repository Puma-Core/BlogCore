## Why

The production deployment needs an explicit way to trust its public origin for Django CSRF validation. In addition, public API endpoints must remain available in production without being included in generated OpenAPI documentation.

## What Changes

- Configure `CSRF_TRUSTED_ORIGINS` from an environment variable with a localhost development default.
- Document the CSRF origin setting in the example environment file.
- Exclude public author and post API view sets from the generated OpenAPI schema in production while preserving their runtime routes.
- Keep format-suffixed router routes available only in development.

## Capabilities

### New Capabilities
- `production-api-documentation`: controls OpenAPI visibility for public API endpoints by environment without removing the endpoints themselves.

### Modified Capabilities
- `project-foundation`: extends runtime environment configuration to include trusted CSRF origins.

## Impact

- Affected code: `project/app/settings.py`, `project/app/router.py`, public API view sets, and `.env.example`.
- Affected behavior: production CSRF validation and generated OpenAPI schemas.
- Dependencies: no new dependencies.
