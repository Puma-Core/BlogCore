## Purpose

Keep public API routes usable in every environment while preventing production OpenAPI output from disclosing their contract or development-only URL variants.

## ADDED Requirements

### Requirement: Production schema excludes public API routes
When the application runs in production, generated OpenAPI output SHALL exclude the public author-detail and author-post routes. This exclusion SHALL NOT remove or change the runtime availability of those routes.

#### Scenario: Schema generation in production
- **WHEN** an OpenAPI schema is generated with `ENVIRONMENT=production`
- **THEN** it contains no paths for the public author-detail or author-post routes

#### Scenario: Public API remains available in production
- **WHEN** the application runs with `ENVIRONMENT=production` and a client requests an existing public author or post resource
- **THEN** the corresponding API route remains resolvable and responds according to its public endpoint contract

### Requirement: Format suffixes are development-only
The router SHALL expose format-suffixed API routes only when the application runs in development.

#### Scenario: Development format suffix route
- **WHEN** the application runs with `ENVIRONMENT=development`
- **THEN** a public API route with a supported format suffix is resolvable

#### Scenario: Production format suffix route
- **WHEN** the application runs with `ENVIRONMENT=production`
- **THEN** the equivalent format-suffixed public API route is not resolvable
