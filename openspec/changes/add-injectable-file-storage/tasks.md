## 1. Storage Dependencies And Configuration

- [ ] 1.1 Add the maintained Django S3 storage integration and its `boto3` dependency to the project, then verify `uv sync` completes successfully.
- [ ] 1.2 Extend Django media settings to build `STORAGES["default"]` from the selected backend and injected bucket, region, endpoint, credential, domain, and signing options, then verify default local settings still resolve to `FileSystemStorage`.
- [ ] 1.3 Validate required remote bucket configuration when the S3-compatible backend is selected, then verify incomplete remote configuration raises a descriptive settings error rather than selecting local storage.

## 2. FileField Integration And Tests

- [ ] 2.1 Preserve `Attachment.file` as a standard `FileField` using the default Django storage, then verify attachment upload, URL, and delete paths do not introduce service-specific model or view code.
- [ ] 2.2 Add database-free configuration tests for local default, custom endpoint with explicit credentials, and ambient credentials, then verify them with `uv run pytest project/tests/unit_test/attachments`.
- [ ] 2.3 Add a mocked remote-storage delegation test covering an attachment file operation, then verify no cloud credentials, bucket, or network connection is required.

## 3. Verification And Deployment Guidance

- [ ] 3.1 Document the remote media environment variables and their local defaults without exposing secrets, then verify the documented S3-compatible configuration maps to the generated storage options.
- [ ] 3.2 Run `uv run python project/manage.py check` and the attachment test suite, then verify both commands pass with the default local configuration.
