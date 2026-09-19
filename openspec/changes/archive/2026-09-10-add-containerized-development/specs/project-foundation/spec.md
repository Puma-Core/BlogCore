## ADDED Requirements

### Requirement: Configurable permitted hosts
The project SHALL derive its permitted HTTP host names and addresses from an environment variable while retaining localhost and 127.0.0.1 as development defaults when the variable is unset.

#### Scenario: Default local host access
- **WHEN** no permitted-host environment variable is configured
- **THEN** requests addressed to `localhost` and `127.0.0.1` are accepted in development

#### Scenario: External container access
- **WHEN** a permitted-host environment variable includes an external host name or address
- **THEN** requests using that host name or address are accepted by the Django application

### Requirement: Configurable runtime settings
The project SHALL derive its secret key, debug mode, environment name, and API base URL from environment variables. SQLite SHALL remain the default database when no database configuration is supplied.

#### Scenario: Container runtime configuration
- **WHEN** the container supplies values for the runtime-setting environment variables
- **THEN** Django uses those values while retaining SQLite as its database
