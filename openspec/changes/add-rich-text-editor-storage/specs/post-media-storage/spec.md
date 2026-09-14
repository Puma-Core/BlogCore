## ADDED Requirements

### Requirement: Authenticated authors can upload supported images
The system MUST expose an authenticated upload operation for post-editor image attachments and MUST accept only configured image MIME types below a configurable maximum size.

#### Scenario: Valid image upload
- **WHEN** an authenticated author uploads a supported image within the size limit
- **THEN** the system stores it through Django's configured storage backend
- **AND** creates an attachment record owned by that author
- **AND** returns a Vditor-compatible success response containing the attachment identifier and usable URL.

#### Scenario: Anonymous upload
- **WHEN** an unauthenticated client uploads a file
- **THEN** the system rejects the request with an authentication error
- **AND** does not write a file or attachment record.

#### Scenario: Unsupported or oversized upload
- **WHEN** a client uploads a non-image file, an image with a disallowed MIME type, or a file exceeding the configured limit
- **THEN** the system rejects the request with a validation error
- **AND** does not leave a stored attachment behind.

### Requirement: Stored files have controlled identity and ownership
The system MUST generate the storage path/name for each attachment and MUST retain original name, MIME type, size, owner, timestamps, and optional post association as metadata.

#### Scenario: Filename collision
- **WHEN** two authors upload files with the same original filename
- **THEN** each attachment receives a distinct server-controlled storage identity
- **AND** neither upload overwrites the other.

#### Scenario: Attachment is assigned to a post
- **WHEN** an owned attachment is associated with a post
- **THEN** the system verifies that the requesting author may edit that post
- **AND** stores the post relation without changing the file URL.

### Requirement: Attachment access is scoped
The system MUST prevent one author from assigning, deleting, or managing another author's attachments, and MUST not expose management operations without the required authorization.

#### Scenario: Cross-author management request
- **WHEN** an author attempts to associate or delete an attachment owned by another author
- **THEN** the system rejects the request
- **AND** leaves the attachment and its ownership unchanged.

#### Scenario: Markdown references an uploaded image
- **WHEN** Vditor inserts the URL returned for a successful upload into post Markdown
- **THEN** the saved Markdown contains a stable reference to that stored file
- **AND** the reference remains valid through the configured media storage/delivery mechanism.

### Requirement: Media storage is configurable
The system MUST use Django's storage abstraction and MUST support separate development defaults and production-configured media storage/delivery settings.

#### Scenario: Development configuration
- **WHEN** the application runs with default development settings
- **THEN** uploaded media uses the configured local media root and URL
- **AND** media routes are available for local development without changing application code.

#### Scenario: Production configuration
- **WHEN** a deployment supplies durable media storage and media URL settings
- **THEN** attachment URLs are generated from that configuration
- **AND** application code does not require a filesystem-specific path.
