## Why

The platform needs a defined path for a Django user to sign in to the
administration site and review the posts stored in the database. The existing
`Post` registration needs explicit validation of its local configuration.

## What Changes

- Define authenticated access to the Django administration site for staff users.
- Define how registered `Post` records are presented in the administration list.
- Validate the project's `Post` administration configuration without duplicating
  Django framework coverage.

## Capabilities

### New Capabilities
- `django-admin-post-access`: Authenticated staff access to the Django admin and
  visibility of persisted posts.

### Modified Capabilities

- None.

## Impact

- `project/posts/admin.py`.
- Django's built-in authentication and admin URLs.
