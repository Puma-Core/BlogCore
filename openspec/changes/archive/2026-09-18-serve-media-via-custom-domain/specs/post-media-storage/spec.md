## MODIFIED Requirements

### Requirement: Media storage is configurable
The system MUST use Django's storage abstraction and MUST support separate development defaults and production-configured media storage/delivery settings. For S3-compatible remote storage, the deployment MUST be able to configure a custom media domain and disable query-string authentication so that generated attachment URLs are public, stable, and served through that domain.

#### Scenario: Development configuration
- **WHEN** the application runs with default development settings
- **THEN** uploaded media uses the configured local media root and URL
- **AND** media routes are available for local development without changing application code.

#### Scenario: Production configuration
- **WHEN** a deployment supplies durable media storage and media URL settings
- **THEN** attachment URLs are generated from that configuration
- **AND** application code does not require a filesystem-specific path.

#### Scenario: Public remote media delivery
- **WHEN** a deployment configures S3-compatible storage with a custom media domain and query-string authentication disabled
- **THEN** uploaded attachment URLs use the configured custom media domain
- **AND** the URLs contain no time-limited signature or expiration query parameters
- **AND** the URLs remain suitable for persistent Markdown references while the object remains available in storage.

#### Scenario: Public object read access
- **WHEN** a client requests an attachment URL generated for public remote media delivery
- **THEN** the custom media domain serves the stored object without requiring bucket-service request signing
- **AND** the application continues to require authentication for attachment upload and management operations.
