## Context

`Post` currently stores title, content, timestamps, and a foreign key to `PublicProfile`, but it has no URL-safe identifier and the posts app has no API views. The API already uses Django REST framework, a `DefaultRouter`, and public author lookup by `public_username`. See `proposal.md` and the delta specs for the observable contract.

## Goals / Non-Goals

**Goals:**

- Add a persisted, normalized identifier generated from the post title.
- Enforce uniqueness at the database boundary for `(author, unique_name)`.
- Provide public read-only collection and detail resources scoped by `public_username`.
- Keep serializers explicit and prevent private user data or unrelated relationships from entering the response.
- Test slug generation, title changes, collisions, ORM constraints, serialization, routing, anonymous access, and author scoping.

**Non-Goals:**

- No post creation or editing API; staff administration remains the write path.
- No global post listing, ID-based lookup, search, pagination, filtering beyond the author path, or comments.
- No changes to public-profile onboarding, author details, client authentication, or authorization policy.
- No automatic suffixing of colliding slugs, since that makes URLs depend on creation order and weakens the title-derived identifier contract.

## Decisions

### Persist the derived identifier on `Post`

Add a non-null character field such as `unique_name` and generate it from `title` during model save using the project's slug normalization utilities or an equivalent deterministic normalization. Persisting it makes lookup/indexing efficient and gives the database a concrete field on which to enforce `UniqueConstraint(fields=("author", "unique_name"))`. Computing only at request time was rejected because it would not protect historical links or uniqueness under concurrent writes.

Existing rows require a data migration that derives identifiers from their titles. If two existing posts for one author normalize to the same value, the migration must fail clearly and require manual title/identifier resolution rather than inventing suffixes.

### Scope post lookup through the public username

Expose collection and detail routes under `/api/authors/<public_username>/posts/`. The view queryset first resolves the public profile and then scopes posts to it; detail lookup uses `unique_name` inside that scoped queryset. This prevents a valid slug belonging to another author from being returned. A nested route was chosen over a global `/posts/<unique_name>/` route because the identifier is intentionally unique per author, not globally.

### Use distinct read serializers and database previews

Use separate explicit serializers for the collection and detail responses. The collection serializer exposes `unique_name`, title, `content_preview`, `created_at`, and `author_full_name`; the detail serializer exposes the complete content and the public author identity. The collection queryset will annotate `content_preview` with a database substring expression limited to 256 characters before serialization, so it never selects complete post bodies merely to truncate them in Python. Do not serialize the complete model or the related user.

### Keep public routes independent of environment

Register the post routes alongside the existing public author route, outside the development-only browsable login and schema routes. Use read-only DRF behavior and allow anonymous GET access; unsupported methods must not create or mutate posts.

### Test behavior at the smallest useful boundary

Place model and serializer tests under the posts unit-test area, using in-memory instances or mocked managers when persistence is unnecessary. Test the collection serializer's exact summary fields and assert the queryset annotates the preview through a database substring expression limited to 256 characters. Use database-backed tests only for migration/constraint and ORM lookup behavior. Add routing and endpoint tests for both author collection and nested detail, including a cross-author slug mismatch and production-style URL registration.

## Risks / Trade-offs

- **Existing titles can normalize to duplicate identifiers** -> Run the data migration transactionally and fail with an actionable conflict instead of silently changing links.
- **Title edits can break existing article URLs** -> Treat the derived identifier as title-coupled per the requested behavior; link stability across title edits can be addressed by a future immutable alias capability.
- **Public listings load article content unnecessarily** -> Produce the 256-character preview in the database query and serialize only that annotation; reserve full content for the detail resource.
- **Concurrent creates can race before model validation** -> Keep the database uniqueness constraint authoritative and translate integrity failures into the API/model validation behavior selected during implementation.

## Migration Plan

1. Add the field and deterministic data migration, resolving any pre-existing title collisions before applying the uniqueness constraint.
2. Add the composite database constraint and verify `manage.py check` plus migration tests.
3. Add serializers, nested read-only routes, and their unit/integration tests.
4. Run the relevant posts tests and the full suite.
5. Roll back by removing the routes and application code, then reverting the migration only if no dependent links or data need to be preserved.
