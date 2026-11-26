## Purpose

Allow authorized staff users to access Django administration and review every
persisted blog post through the registered post list.

## ADDED Requirements

### Requirement: Staff user can access administration
The system SHALL allow an authenticated staff user with valid Django credentials
to access the administration site. It MUST redirect unauthenticated requests to
the administration login page and deny administration access to users without
staff privileges.

#### Scenario: Staff user signs in successfully
- **WHEN** a staff user submits valid credentials on the administration login page
- **THEN** the user can access the administration index

#### Scenario: Unauthenticated user requests administration
- **WHEN** an unauthenticated user requests an administration page
- **THEN** the system redirects the user to the administration login page

### Requirement: Staff user can view published posts in administration
The system SHALL show a staff user the registered post list in administration,
including each persisted post's title and creation timestamp.

#### Scenario: Post list contains persisted posts
- **WHEN** a staff user opens the post list after posts exist in the database
- **THEN** the list displays every persisted post with its title and creation timestamp
