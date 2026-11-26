## 1. Foundation

- [x] 1.1 Create the `profiles` Django application and register it in project settings.
- [x] 1.2 Create test fixtures and factories for users, variables, social network configurations, instances, and public profiles.

## 2. Reusable variables and instances

- [x] 2.1 [RED] Add failing model tests for variable labels, descriptions, regular-expression validation, parent social-network-instance ownership, and archiving.
- [x] 2.2 [GREEN] Implement variables and variable instances with model-level validation, parent-derived ownership, and archival behavior.
- [x] 2.3 [REFACTOR] Simplify variable validation, parent-derived ownership, and archival handling while preserving the passing model tests.
- [x] 2.4 [RED] Add failing admin permission and validation tests for variables.
- [x] 2.5 [GREEN] Register variables in Django admin with staff-only management.

## 3. Social network configurations and instances

- [x] 3.1 [RED] Add failing model tests for social network configurations, `template_url`, `icon_url`, associated variables, permitted variable instances, immutable authors, archival, and URL construction.
- [x] 3.2 [GREEN] Implement social network configurations and user social network instances with validation, immutable author, and archival behavior.
- [x] 3.3 [REFACTOR] Simplify configuration, ownership, archival, and URL-building interfaces while preserving the passing model tests.
- [x] 3.4 [RED] Add failing admin permission and validation tests for social network configurations.
- [x] 3.5 [GREEN] Register social network configurations in Django admin with staff-only management.

## 4. Public profile identity

- [x] 4.1 [RED] Add failing model and form tests for public-profile fields, unique `public_username`, optional valid `photo_url`, and validation errors.
- [x] 4.2 [GREEN] Implement the public profile model and form using `public_username` as the public identifier and `photo_url` as an external image URL.
- [x] 4.3 [REFACTOR] Simplify profile validation and form handling while preserving the passing tests.
- [x] 4.4 Generate and apply the initial migrations for the profiles application.

## 5. User social network dashboard

> Out of scope: no se implementarán vistas, plantillas ni URLs propias del proyecto. La gestión de instancias queda en el modelo y en Django admin.

- [x] 5.1 Add model-level tests for ownership, creation, updating active values, archival, immutable network-instance authors, and rejection of unauthorized changes.
- [x] 5.2 Verify that `SocialNetworkInstance` and `VariableInstance` enforce ownership and archival rules without dashboard views.

## 6. Public presentation

> Out of scope: no se implementarán vistas, plantillas ni URLs propias para la presentación pública. El perfil público se mantiene como modelo de datos.

- [x] 6.1 Add model and form tests for `PublicProfile` fields, unique `public_username`, optional valid `photo_url`, and validation errors.
- [x] 6.2 Verify that `PublicProfile` can be persisted and validated without a public view or template.

## 7. Final verification

- [x] 7.1 Run the complete profiles test suite and resolve any regressions.
- [x] 7.2 Run Django migrations and `uv run python project/manage.py check`.

For an unplanned task discovered in an implementation child branch, record it as `+=<número>` in that branch's execution tracking without renumbering this approved plan.
