## 1. Dependency And Storage Configuration

- [x] 1.1 Confirm the Django Vditor package/API supports Django 6.1 and Markdown output; add the dependency or implement the smallest local widget integration and document the choice.
- [x] 1.2 Add environment-aware `MEDIA_ROOT`, `MEDIA_URL`, and storage settings, development media serving, upload limits, and support only JPEG/JPG and WebP MIME types.
- [x] 1.3 Add the independent `attachments` app and its `Attachment` model with a server-controlled upload path, ownership metadata, JSON metadata, indexes/constraints, and migrations; add database-free model/validation tests in `project/tests/unit_test/attachments/` where possible.

## 2. Attachment Upload And Authorization

- [ ] 2.1 Implement the authenticated Vditor-compatible image upload endpoint with JPEG/JPG and WebP MIME/size validation, optional JSON metadata preservation, storage cleanup on validation failure, and stable attachment URL/identifier responses.
- [ ] 2.2 Implement attachment management authorization so only the owning author can manage or delete files, without using metadata relationship references for authorization.
- [ ] 2.3 Add route and endpoint tests in `project/tests/unit_test/attachments/` for anonymous access, valid JPEG/JPG and WebP uploads, invalid MIME types, oversized files, filename collisions, cross-author access, metadata references, and generated URLs.

## 3. Markdown Editor Integration

- [ ] 3.1 Add the post `ModelForm`/admin widget integration, initialize Vditor with stored Markdown and the upload endpoint, and preserve existing post validation and author permissions.
- [ ] 3.2 Add form/admin tests in `project/tests/unit_test/posts/` proving existing Markdown loads unchanged, formatted content is persisted as Markdown, and upload references can be saved in `Post.content`.
- [ ] 3.3 Verify existing serializers and public post endpoints continue returning canonical Markdown without changing identifiers or response contracts.

## 4. Verification And Operations

- [ ] 4.1 Run `uv run python project/manage.py makemigrations` and `uv run python project/manage.py check`; inspect generated migrations and media configuration.
- [ ] 4.2 Run the relevant posts tests and then `uv run pytest` for the full suite.
- [ ] 4.3 Document production media storage, delivery, size/type limits, and the behavior of unreferenced draft attachments.
