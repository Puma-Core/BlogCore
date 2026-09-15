## Context

The current settings expose `MEDIA_STORAGE_BACKEND` and configure it as Django's default storage, with `FileSystemStorage` as the local default. `Attachment.file` already delegates persistence to that default `FileField` storage. See `proposal.md` for motivation and the delta specs for behavior.

## Goals / Non-Goals

**Goals:**

- Preserve the existing `FileField` contract for attachment operations across local and remote storage.
- Provide one explicit settings boundary for remote S3-compatible client options.
- Support AWS S3 and endpoint-compatible services without embedding provider details in models or views.
- Make configuration behavior testable without remote network calls.

**Non-Goals:**

- Adding provider-specific attachment models, upload endpoints, or direct `boto3` calls in application views.
- Migrating existing local files to an object-storage bucket.
- Provisioning buckets, managing IAM policies, or generating CDN configuration.
- Supporting separate storage backends per attachment type in this change.

## Decisions

### Configure Django's default storage with backend options

Keep `Attachment.file` unchanged and build `STORAGES["default"]` from `MEDIA_STORAGE_BACKEND` plus a settings-derived options mapping. The local default continues to use `FileSystemStorage`. For S3-compatible deployments, select the `django-storages` S3 backend and provide its bucket and `boto3` client options through `OPTIONS`.

This follows Django's storage abstraction and lets every `FileField` use the same interface. Direct `boto3` calls from the attachment app were rejected because they would duplicate storage semantics and prevent local storage from sharing the path.

### Define an explicit environment-to-client configuration boundary

Add environment-backed settings for the bucket, region, optional endpoint URL, optional explicit access key/secret/session token, URL domain, and URL signing behavior. Build the backend options in settings, omitting unset optional credential values so the SDK's ambient credential chain remains available.

The selected backend remains configurable by import path to retain the existing deployment escape hatch. A custom storage wrapper was considered but rejected: the maintained S3 backend already translates Django storage operations to `boto3` and accepts the required client parameters.

### Fail configuration errors rather than changing persistence targets

Validate that the remote backend has the required bucket setting while loading configuration. A selected remote backend with incomplete required configuration raises a clear settings error instead of resolving to local storage, which could place production data in an unintended location.

### Test settings and storage delegation in isolation

Unit tests will assert backend selection and the generated options mapping for local, explicit-credential, custom-endpoint, and ambient-credential configurations. Storage calls will mock the S3 backend/client boundary; tests will not require cloud credentials, buckets, or network access.

## Risks / Trade-offs

- [Credentials supplied through environment variables can be exposed in deployment logs] -> Do not log storage options or credential values; document use of secret injection or ambient credentials.
- [S3-compatible services differ in URL and signing expectations] -> Expose endpoint, custom-domain, and signing configuration while leaving provider policy under deployment control.
- [An invalid remote configuration prevents startup] -> Fail early with a descriptive error rather than storing files locally by accident.
- [The S3 dependency increases the production dependency surface] -> Add the maintained Django S3 integration and pin it through the existing dependency workflow.

## Migration Plan

1. Add the S3 storage dependency and configuration settings while retaining the local default.
2. Deploy with no remote settings to verify existing local behavior is unchanged.
3. Provision and validate the target bucket and credentials, then enable the remote backend and its options in the deployment environment.
4. New uploads use the selected backend; migrate historical local files separately if required.
5. Roll back by restoring the local backend configuration. Objects written remotely remain remote and require an explicit migration to become locally available.
