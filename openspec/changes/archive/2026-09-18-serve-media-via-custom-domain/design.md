## Context

See `proposal.md` for motivation. Attachments use Django's default storage and expose `FileField.url` in the upload and detail responses. The project already accepts S3-compatible endpoint, bucket, region, addressing style, and credential configuration, while local development uses filesystem storage. The deployment needs publicly readable objects through a custom media domain rather than presigned bucket URLs.

## Goals / Non-Goals

**Goals:**
- Generate stable public attachment URLs from a configured custom media domain when S3-compatible storage is selected.
- Make the URL-signing policy explicit and configurable with a public-delivery default for the container deployment.
- Preserve local storage behavior and authenticated attachment management.

**Non-Goals:**
- Provision the bucket, DNS record, TLS certificate, CDN, or bucket access policy.
- Change supported attachment types, upload validation, object paths, or database records.
- Make upload or attachment-management APIs public.

## Decisions

### Configure public delivery at the storage backend

Pass the custom domain and query-string authentication settings to the selected S3-compatible Django storage backend. `FileField.url` then becomes the single source for upload and detail responses, so there is no URL rewriting in views. This preserves the storage abstraction and applies consistently anywhere attachment URLs are generated.

An alternative is to rewrite bucket URLs in the attachment API. That would leave other `FileField.url` consumers inconsistent and couples application code to a delivery provider, so it is rejected.

### Use unsigned object URLs for this public-media use case

Set query-string authentication to false for the remote backend used for public attachments. The custom domain and its backing bucket/CDN must permit anonymous reads. This removes the one-hour signature expiry from Markdown references while retaining server credentials for upload and deletion.

An alternative is to extend presigned-URL expiry. It only postpones broken document images and cannot produce persistent references, so it is rejected.

### Keep backend selection and settings validation aligned

Use one supported S3-compatible backend identifier consistently in settings validation, storage options, example configuration, and tests. Continue accepting endpoint, region, bucket, credentials, and addressing style through environment configuration; add the custom domain and query-string-authentication variables to that same contract.

An alternative is a provider-specific storage class. It would reduce compatibility with the project's existing S3-compatible endpoint configuration, so it is rejected.

## Risks / Trade-offs

- [The custom domain or bucket does not allow anonymous reads] -> Validate a deployed attachment URL after configuring the bucket/CDN policy; uploads continue to succeed but reads will fail until infrastructure is corrected.
- [A custom domain is configured with an invalid scheme or path] -> Document the expected domain value and test that the storage backend receives it unchanged.
- [Unsigned URLs expose media to anyone with the URL] -> Limit this behavior to the intended public attachment bucket/prefix; private assets require a separate storage/delivery contract.
- [The selected backend identifier differs across environments] -> Cover the selected backend and its options with isolated configuration tests.

## Migration Plan

1. Add the custom-domain and unsigned-URL storage options, then test generated remote URLs without contacting a bucket.
2. Configure the production custom media domain, DNS/TLS, and public-read policy before deploying the application change.
3. Deploy and verify a newly uploaded image renders from the custom domain after more than the previous signature lifetime.
4. Roll back by restoring the prior application configuration and enabling query-string authentication; existing Markdown references will again depend on signed URL expiry.
