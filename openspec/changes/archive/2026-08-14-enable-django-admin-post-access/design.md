## Context

The `Post` model is already registered in Django administration with title and
creation timestamp columns. Django provides the administration routes,
authentication, permissions, and model behavior; this change validates only the
project's local administration configuration.

## Goals / Non-Goals

**Goals:**
- Verify the registered `PostAdmin` list configuration and staff access setting.
- Keep Django's standard administration URL and authentication flow unchanged.

**Non-Goals:**
- Add public post browsing, custom login pages, or new authorization roles.
- Change the `Post` database schema or create users automatically.
- Duplicate Django framework tests for administration routes, authentication, or
  model behavior.

## Decisions

- Rely on Django's built-in administration authentication and staff permission
  checks rather than custom middleware or duplicate framework tests.
- Validate the registered `PostAdmin` configuration directly. This covers the
  local customization without testing Django's own routes or model internals.

## Risks / Trade-offs

- [Django behavior is not re-tested locally] -> Review Django upgrade notes and
  perform a manual administration smoke test when upgrading the framework.
- [Local admin configuration can regress] -> Retain direct validation of the
  registered `PostAdmin` list configuration.

## Migration Plan

No data migration is required. Rollback consists of reverting the local
administration configuration change if one is introduced later.
