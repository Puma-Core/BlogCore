## MODIFIED Requirements

### Requirement: Configurable runtime settings
The project SHALL derive its secret key, debug mode, environment name, API base URL, and trusted CSRF origins from environment variables. SQLite SHALL remain the default database when no database configuration is supplied. When the trusted-CSRF-origins variable is unset, the project SHALL trust the localhost HTTP origin for development.

#### Scenario: Container runtime configuration
- **WHEN** the container supplies values for the runtime-setting environment variables
- **THEN** Django uses those values, including the configured trusted CSRF origins, while retaining SQLite as its database

#### Scenario: Default CSRF origin for local development
- **WHEN** no trusted-CSRF-origins environment variable is configured
- **THEN** Django trusts `http://localhost` for CSRF validation
