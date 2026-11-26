## Purpose

Provides a single configurable media-storage contract for local files and S3-compatible object storage without changing application file models.

## ADDED Requirements

### Requirement: Media backend is selected by configuration
The system MUST select its default Django media storage backend from deployment configuration. When no remote backend is configured, it MUST use local filesystem storage; when an S3-compatible backend is configured, it MUST use that backend without application-model changes.

#### Scenario: Default local storage
- **WHEN** the application starts without remote media-storage configuration
- **THEN** the default media backend stores files under the configured local media root
- **AND** generated media URLs use the configured local media URL.

#### Scenario: Configured remote storage
- **WHEN** a deployment configures the S3-compatible media backend
- **THEN** the default media backend persists media objects to the configured remote bucket
- **AND** generated file URLs are supplied by that backend.

### Requirement: Remote storage client parameters are injectable
The system MUST accept remote object-storage client parameters from Django configuration, including bucket, region, endpoint, and supported credential values. It MUST pass the configured values to the remote storage client without hard-coding a provider endpoint or credentials in application code.

#### Scenario: S3-compatible endpoint configuration
- **WHEN** a deployment supplies a bucket, region, custom endpoint, and credentials
- **THEN** the remote storage client uses those supplied values
- **AND** file uploads target the configured bucket and endpoint.

#### Scenario: Ambient credentials
- **WHEN** a deployment configures a bucket and region but omits explicit credentials
- **THEN** the remote storage client uses its supported ambient credential provider chain
- **AND** application configuration does not require placeholder credential values.

#### Scenario: Invalid remote configuration
- **WHEN** the selected remote media backend lacks required bucket configuration
- **THEN** application configuration fails clearly
- **AND** the application does not silently fall back to local storage.
