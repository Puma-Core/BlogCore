## Purpose

Permitir que el blog registre clientes externos que acceden a recursos protegidos mediante un secreto único, dominios permitidos y permisos de Django, todo gestionable desde el panel de administración.

## ADDED Requirements

### Requirement: Client persistence

The system SHALL persist API clients. A client SHALL have a unique human-readable name, a list of allowed domains, a unique secret token, an active flag, optional Django groups, optional Django permissions, and creation/update timestamps.

#### Scenario: Creating a client

- **WHEN** a developer creates a `Client` through the ORM providing a name and a valid domain list
- **THEN** the client is stored in the database with the provided name, domain list, an automatically generated secret, `is_active` set to `True`, and the current creation/update timestamps

#### Scenario: Client name uniqueness

- **WHEN** a developer attempts to create two clients with the same name
- **THEN** the second creation is rejected with a uniqueness violation

### Requirement: Secret generation

The system SHALL generate a unique, non-empty secret token for every client that is created without an explicit secret. The secret SHALL be treated as sensitive data.

#### Scenario: Secret generated on creation

- **WHEN** a `Client` is created without providing a secret
- **THEN** the system assigns a generated secret that is unique and not empty

#### Scenario: Secret preserved when provided

- **WHEN** a `Client` is created with an explicit secret
- **THEN** the system stores the provided secret unchanged

### Requirement: Domain validation

The system SHALL validate that the `domain` field contains one or more valid URLs separated by commas. Each URL MUST include a protocol and a hostname.

#### Scenario: Valid single domain

- **WHEN** a client is saved with `domain` set to `https://example.com`
- **THEN** the validation succeeds

#### Scenario: Valid multiple domains

- **WHEN** a client is saved with `domain` set to `https://example.com,http://app.example.org`
- **THEN** the validation succeeds

#### Scenario: Invalid domain missing protocol

- **WHEN** a client is saved with `domain` set to `example.com`
- **THEN** the validation fails with a descriptive error

#### Scenario: Invalid domain empty entry

- **WHEN** a client is saved with `domain` set to `https://example.com,`
- **THEN** the validation fails with a descriptive error

### Requirement: Admin secret visibility

The system SHALL expose clients through the Django admin interface so that authenticated staff can create, view, edit, and delete them. The secret token SHALL be visible only during creation or editing and SHALL be hidden from the changelist and from readonly views after saving.

#### Scenario: Secret visible during creation

- **WHEN** a staff user opens the add form for a client in `/admin/`
- **THEN** the secret field is present and, if left blank, a generated secret is shown before saving

#### Scenario: Secret visible during editing

- **WHEN** a staff user opens the change form for an existing client in `/admin/`
- **THEN** the secret field is visible and editable

#### Scenario: Secret hidden in changelist

- **WHEN** a staff user opens the client changelist in `/admin/`
- **THEN** no secret values are displayed in the list

### Requirement: Client permission helpers

The system SHALL provide methods on `Client` to query Django permissions directly assigned or inherited through groups, and to validate whether a request origin is among the allowed domains.

#### Scenario: Direct permission check

- **WHEN** `has_perm` is called with a permission codename assigned directly to the client
- **THEN** the method returns `True`

#### Scenario: Group permission check

- **WHEN** `has_perm` is called with a permission codename assigned to one of the client's groups
- **THEN** the method returns `True`

#### Scenario: Missing permission check

- **WHEN** `has_perm` is called with a permission codename that is neither assigned to the client nor to its groups
- **THEN** the method returns `False`

#### Scenario: Allowed domain check

- **WHEN** `is_domain_allowed` is called with a hostname present in the client's domain list
- **THEN** the method returns `True`

#### Scenario: Disallowed domain check

- **WHEN** `is_domain_allowed` is called with a hostname not present in the client's domain list
- **THEN** the method returns `False`
