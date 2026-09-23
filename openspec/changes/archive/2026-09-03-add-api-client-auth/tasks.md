## 1. App and Model

- [x] 1.1 Create the `clients` Django app inside `project/`.
- [x] 1.2 Define the `Client` model with fields: `name`, `domain`, `secret`, `is_active`, `groups`, `permissions`, `created_at`, `updated_at`.
- [x] 1.3 Implement automatic `secret` generation when the field is blank.
- [x] 1.4 Add `Meta` options for ordering and verbose names.
- [x] 1.5 Generate the initial migration for `clients`.
- [x] 1.6 Register `clients` in `INSTALLED_APPS`.
- [x] 1.7 Add pytest unit tests for `Client` creation, secret generation and name uniqueness.

## 2. Validators and Model Helpers

- [x] 2.1 Create a validator that ensures `domain` is a comma-separated list of valid URLs with protocol.
- [x] 2.2 Implement `Client.is_domain_allowed(host)` to check a hostname against the allowed list.
- [x] 2.3 Implement `Client.has_perm(codename)` covering direct and group permissions.
- [x] 2.4 Implement `Client.has_module_perms(app_label)`.
- [x] 2.5 Add pytest unit tests for domain validation (valid single/multiple, missing protocol, empty entry).
- [x] 2.6 Add pytest unit tests for permission helpers (`has_perm`, `has_module_perms`) and `is_domain_allowed`.

## 3. Django Admin

- [x] 3.1 Create a custom admin form that generates and displays the `secret` when it is blank.
- [x] 3.2 Configure `ClientAdmin` with list display, filters, search and exclude `secret` from readonly/changelist views.
- [x] 3.3 Ensure the secret field is visible only on add/change forms and hidden from the changelist.
- [x] 3.4 Add pytest unit tests for admin configuration (secret not in list display, form behavior).

## 4. Validation and Checks

- [x] 4.1 Run `uv run python project/manage.py makemigrations`, `uv run python project/manage.py migrate`, `uv run python project/manage.py check` and `uv run pytest`.
