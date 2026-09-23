## Purpose

Lets authors securely upload supported post images while preserving portable Markdown references.

## Requirements

### Requirement: Authenticated authors can upload supported images
The system MUST expose an authenticated upload operation for post-editor image attachments and MUST accept only `image/jpeg` (for `.jpg` and `.jpeg`) and `image/webp` below a configurable maximum size.

#### Scenario: Valid JPEG/JPG or WebP upload
- **WHEN** an authenticated author uploads a JPEG/JPG or WebP image within the size limit
- **THEN** the system stores it through Django's configured storage backend
- **AND** creates an attachment record owned by that author
- **AND** returns a Vditor-compatible success response containing the attachment identifier and usable URL.

#### Scenario: Anonymous upload
- **WHEN** an unauthenticated client uploads a file
- **THEN** the system rejects the request with an authentication error
- **AND** does not write a file or attachment record.

#### Scenario: Unsupported or oversized upload
- **WHEN** a client uploads a non-image file, a PNG, GIF, or another image with a disallowed MIME type, or a file exceeding the configured limit
- **THEN** the system rejects the request with a validation error
- **AND** does not leave a stored attachment behind.

### Requirement: Stored files have controlled identity and ownership
The system MUST generate the storage path/name for each attachment and MUST retain original name, MIME type, size, owner, timestamps, and an extensible metadata object.

#### Scenario: Filename collision
- **WHEN** two authors upload files with the same original filename
- **THEN** each attachment receives a distinct server-controlled storage identity
- **AND** neither upload overwrites the other.

#### Scenario: Metadata records a dynamic post reference
- **WHEN** an attachment metadata object includes `relationship.posts` with post identifiers
- **THEN** the system preserves those identifiers in the attachment metadata
- **AND** does not create a database relationship between the attachment and posts.

### Requirement: Attachment access is scoped
The system MUST prevent one author from deleting or managing another author's attachments, and MUST not expose management operations without the required authorization. Metadata relationship references MUST NOT grant access to an attachment.

#### Scenario: Cross-author management request
- **WHEN** an author attempts to delete or manage an attachment owned by another author
- **THEN** the system rejects the request
- **AND** leaves the attachment and its ownership unchanged.

#### Scenario: Markdown references an uploaded image
- **WHEN** Vditor inserts the URL returned for a successful upload into post Markdown
- **THEN** the saved Markdown contains a stable reference to that stored file
- **AND** the reference remains valid through the configured media storage/delivery mechanism.

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
