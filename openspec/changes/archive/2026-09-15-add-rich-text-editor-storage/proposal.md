## Why

Post content is currently edited and stored as an unstructured text field. This limits authors to plain text and provides no consistent way to embed images in an article. The blog needs a Markdown-oriented rich text workflow so authors can compose formatted posts while keeping the persisted representation portable and easy to render through the existing API.

## What Changes

- Integrate a Django Vditor-based editor into the post authoring surface.
- Store the editor output as Markdown in the post content field, preserving Markdown as the canonical representation.
- Add authenticated attachment upload handling backed by Django's storage abstraction.
- Persist metadata for uploaded files and associate each file with its author.
- Return a stable file reference/URL from uploads so Vditor can insert the selected image into Markdown.
- Validate JPEG/JPG and WebP image types, size, and ownership, and prevent unauthorized files from being managed through the authoring workflow.
- Add configuration for media storage and tests covering editor integration, Markdown persistence, upload authorization, and file references.

## Capabilities

### New Capabilities

- `rich-text-post-editor`: authors edit posts with Vditor and persist Markdown content.
- `post-media-storage`: authors upload and reference image attachments through a controlled storage API.

### Modified Capabilities

- `post-model`: the existing content field becomes explicitly Markdown-backed without changing the public post identifier contract.

## Impact

- Affected code: a new `project/attachments` app, `project/posts` editor integration, Django settings and URLs, dependency configuration, media storage configuration, migrations, and tests.
- Affected behavior: post administration/authoring, independent attachment upload flow, and the representation of post content returned by existing APIs.
- Dependencies: a Django Vditor integration and its frontend assets; the implementation must confirm the selected package supports Django 6.1 and Markdown output before adoption.
- Operational requirement: deployments must provide a durable `MEDIA_ROOT`/`MEDIA_URL` or a configured Django storage backend; local filesystem storage is sufficient for development.
