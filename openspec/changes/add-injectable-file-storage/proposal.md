## Why

The application can select a Django storage backend, but it has no standard way to configure a `boto3` client for remote object storage. Deployments therefore cannot switch between local media and externally hosted files using one documented configuration contract.

## What Changes

- Add a configurable S3-compatible Django storage backend backed by `boto3`.
- Define settings for selecting the media backend and supplying the remote storage client parameters, including credentials, endpoint, region, and bucket settings.
- Keep `Attachment.file` as a standard Django `FileField` so uploads, URLs, reads, and deletes use the same model API with local or remote storage.
- Retain local filesystem storage as the default when no remote backend is selected.

## Capabilities

### New Capabilities
- `injectable-media-storage`: Configures an S3-compatible media storage backend whose `boto3` client is constructed from injected Django settings.

### Modified Capabilities
- `post-media-storage`: Require attachment `FileField` storage to work through the same Django storage abstraction for both local and externally configured backends.

## Impact

- Affected code: Django settings, storage configuration, attachment storage tests, and deployment environment documentation.
- Dependencies: `boto3` and the Django S3 storage integration required to expose the configured backend.
- Systems: local media development and S3-compatible object storage deployments.
