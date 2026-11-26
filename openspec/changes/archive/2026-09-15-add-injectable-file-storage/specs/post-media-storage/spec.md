## MODIFIED Requirements

### Requirement: Media storage is configurable
The system MUST use Django's storage abstraction and MUST support separate development defaults and production-configured local or external media storage/delivery settings. `Attachment.file` MUST remain a Django `FileField` whose upload, retrieval, URL generation, and deletion behavior use the selected default storage backend without service-specific model code.

#### Scenario: Development configuration
- **WHEN** the application runs with default development settings
- **THEN** uploaded media uses the configured local media root and URL
- **AND** media routes are available for local development without changing application code.

#### Scenario: Production configuration
- **WHEN** a deployment supplies durable media storage and media URL settings
- **THEN** attachment URLs are generated from that configuration
- **AND** application code does not require a filesystem-specific path.

#### Scenario: Attachment operation with external storage
- **WHEN** an attachment is uploaded, accessed, or deleted while external media storage is selected
- **THEN** its `FileField` delegates the operation to the configured default storage backend
- **AND** the attachment model and upload API use the same contract as with local storage.
