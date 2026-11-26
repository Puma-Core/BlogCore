## Context

See `proposal.md` for motivation. Runtime settings already use environment variables and `get_env_list` for comma-separated configuration. The URL configuration restricts the schema endpoint to development, but schema generation can still inspect registered view sets outside that route. The router currently controls format suffixes separately from the schema endpoint.

## Goals / Non-Goals

**Goals:**
- Make trusted CSRF origins configurable for deployed browser clients.
- Ensure production schema generation omits public API routes while leaving those routes operational.
- Align format-suffix exposure with the development-only documentation surface.

**Non-Goals:**
- Disable Django CSRF middleware or exempt API views from CSRF checks.
- Remove public author or post endpoints in production.
- Add authentication, a documentation UI, or new deployment infrastructure.

## Decisions

### Configure CSRF origins with the existing list-setting convention

Use the existing comma-separated environment-list parsing helper for `CSRF_TRUSTED_ORIGINS`, with `http://localhost` as the development fallback. This supports one or more full origins without introducing a new configuration format. A single raw string is rejected because Django expects a list and deployments can require multiple origins.

### Derive documentation visibility from the configured environment

Use the production environment value to exclude public view sets from OpenAPI schema generation. This protects generated schemas even when invoked outside the development-only schema URL. Restricting only `/api/schema/` is insufficient because a management command or another integration could generate the schema independently.

### Retain runtime routes and restrict only format variants

Keep the existing router registrations unchanged so the public API contracts remain stable. Configure format suffixes only for development, rather than disabling the router or the view sets in production; disabling routes would violate the public endpoint contracts.

## Risks / Trade-offs

- [A deployment provides a host instead of a full URL in `CSRF_TRUSTED_ORIGINS`] -> Document that values must be comma-separated origins including scheme, and validate with Django's system checks.
- [An environment label differs in case or is absent] -> Normalize the environment setting and retain development as the default.
- [Schema consumers need production API documentation] -> Generate and publish the schema from a development or controlled build environment rather than exposing production runtime routes in the schema.

## Migration Plan

1. Add the runtime setting, schema exclusions, and router configuration with tests for development and production behavior.
2. Set `CSRF_TRUSTED_ORIGINS` in each deployed environment to its externally served HTTPS origin before deployment.
3. Deploy normally; rollback by restoring the prior application version and environment configuration if CSRF validation rejects expected browser requests.
