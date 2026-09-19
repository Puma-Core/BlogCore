## 1. Storage Delivery Configuration

- [x] 1.1 Align the supported S3-compatible storage backend identifier, validation, and storage options; verify `uv run python project/manage.py check` succeeds with local defaults.
- [x] 1.2 Add custom media-domain and query-string-authentication environment settings to the remote storage configuration; verify configured S3 storage receives the supplied values without connecting to a remote service.
- [x] 1.3 Configure the container environment so remote media URLs are unsigned by default while preserving an explicit override; verify the rendered environment passes both settings to Django.

## 2. Public Attachment URL Coverage

- [x] 2.1 Add storage configuration tests asserting a custom domain produces an unsigned attachment URL with no signature or expiration query parameters; verify `uv run pytest project/tests/unit_test/attachments/test_storage_configuration.py` passes.
- [x] 2.2 Add upload and attachment-detail tests confirming returned remote attachment URLs use the configured custom media domain; verify the relevant attachment view tests pass.

## 3. Deployment Documentation And Validation

- [x] 3.1 Document the custom media domain, unsigned URL policy, and external public-read prerequisite in `.env.example`; verify the example matches the settings names.
- [x] 3.2 Run `uv run python project/manage.py check` and `uv run pytest project/tests/unit_test/attachments`; verify all checks and targeted tests pass.
