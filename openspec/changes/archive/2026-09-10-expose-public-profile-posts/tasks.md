## 1. Post Identifier And Persistence

- [x] 1.1 Add model tests for title normalization, URL-safe `unique_name`, recalculation after title changes, same-author collisions, and equal slugs across different authors; verify the tests fail before implementation.
- [x] 1.2 Add the persisted `unique_name` field, deterministic title normalization, and model validation/save behavior; verify the model tests pass.
- [x] 1.3 Add the database uniqueness constraint for `(author, unique_name)` and a data migration for existing posts; verify the model constraint behavior and migration configuration are correct.
- [x] 1.4 Resolve or explicitly fail pre-existing normalized title collisions during migration without silently suffixing identifiers; verify the migration error identifies the conflicting author and titles by code review.

## 2. Public Post API Contract

- [x] 2.1 Add serializer tests for the exact collection summary fields, complete detail fields, exclusion of user/account data, and a 256-character preview; verify the serializer tests pass.
- [x] 2.2 Implement distinct collection and detail serializers, with the collection queryset generating `content_preview` through a database substring expression limited to 256 characters; verify each response uses its defined shape without loading full content for the collection preview.
- [x] 2.3 Add endpoint tests for anonymous collection and detail GET requests, missing profiles/posts, cross-author slug mismatches, and unsupported write methods; verify expected HTTP statuses and unchanged data.
- [x] 2.4 Implement public read-only views scoped first by `public_username` and then by `unique_name`; verify endpoint tests pass and no global ID lookup is used.

## 3. Routing And Integration

- [x] 3.1 Add routing tests for `/api/authors/<public_username>/posts/` and `/api/authors/<public_username>/posts/<unique_name>/`, including trailing-slash behavior; verify both routes resolve to the intended views.
- [x] 3.2 Register the nested post routes alongside the existing public author routes while keeping development-only login and schema routes environment-gated; verify routing tests pass in development and production-style settings.
- [x] 3.3 Run `uv run python project/manage.py check` and the relevant posts/API test directories; verify no configuration, import, migration, or routing errors remain.
- [x] 3.4 Run `uv run pytest` for the complete suite and verify all existing author endpoint behavior remains passing.
