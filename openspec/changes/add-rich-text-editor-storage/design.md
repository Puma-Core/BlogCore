## Context

`Post.content` is a Django `TextField` and is exposed by the post serializers. The project has no media configuration or attachment endpoint today. Post administration is currently the only authoring surface, so the editor integration should preserve that workflow unless a reusable form/widget boundary requires a dedicated upload route.

## Goals / Non-Goals

**Goals:**

- Make Markdown the single persisted content format and avoid storing generated HTML as the source of truth.
- Integrate Vditor through a Django form/widget or admin-compatible integration rather than duplicating editor behavior in application templates.
- Give the editor an authenticated upload endpoint that returns the response shape expected by Vditor.
- Store files through Django's `Storage` API, with safe names and metadata that allow files to be associated with their owner and post.
- Make image URLs usable in Markdown and in the existing public post delivery path.
- Keep tests database-light where possible and cover authorization and validation failures.

**Non-Goals:**

- Replacing the existing REST API or changing post slugs and public URL contracts.
- Converting Markdown to HTML at write time or introducing a second canonical content format.
- Supporting arbitrary file types, video processing, image transformations, or a media library UI.
- Adding cloud-provider-specific code; storage providers remain configurable through Django.
- Solving orphan cleanup for every draft lifecycle beyond defining ownership and a future-safe metadata model.

## Decisions

### Markdown remains canonical

Keep `Post.content` as a text field and configure Vditor for Markdown output. Existing Markdown content remains readable, and API consumers continue receiving the canonical text rather than editor-specific HTML. Rendering/sanitization belongs to the eventual presentation layer and is outside this change.

### Use a first-class attachment record

Introduce a media model containing the stored file, original name, MIME type, size, owner, optional post relation, and timestamps. The model provides a stable application-level reference while Django's `FileField` delegates physical persistence to the configured storage backend. The post relation may be assigned after upload when Vditor uploads before the post has been saved.

### Upload through an authenticated, scoped endpoint

Expose a POST endpoint for image uploads using the project's existing authentication and permission conventions. Only authenticated authors may upload; the endpoint validates content type and size, generates a server-controlled path/name, and returns the absolute or configured media URL plus an attachment identifier in the Vditor-compatible response. Retrieval/deletion must enforce owner checks, and public access is limited to files referenced by public posts through normal media serving/storage configuration.

### Integrate at the post form boundary

Use a `ModelForm`/admin widget integration so the editor is present wherever the post authoring form is used. The widget initializes Vditor with Markdown mode and the upload endpoint, while the server continues to validate and save `content` as text. If the chosen Django Vditor package does not support the project's Django version, isolate the Vditor JavaScript initialization in a project widget rather than coupling domain models to a package-specific model.

### Configuration follows Django conventions

Add `MEDIA_URL`, `MEDIA_ROOT`, and storage settings with environment-aware defaults, and serve media in development only. Production deployments must configure durable storage and delivery separately. Do not make application code depend on the local filesystem.

## Risks / Trade-offs

- [The selected Vditor Django package is incompatible with Django 6.1] -> Verify compatibility before adding the dependency; use a small local widget integration with Vditor assets if necessary.
- [Untrusted Markdown renders unsafe HTML or links] -> Keep Markdown canonical but sanitize/secure it at rendering boundaries; do not mark editor output safe by default.
- [Uploads consume excessive storage or bypass type checks] -> Enforce a configurable byte limit, allow only supported image MIME types, use server-generated paths, and test invalid content.
- [An upload is never referenced by a saved post] -> Record ownership and post association separately and document orphan cleanup as a follow-up rather than making deletion unsafe during editing.
- [Public post images are inaccessible in production] -> Make media delivery/storage configuration an explicit deployment requirement and test generated URLs.

## Migration Plan

1. Add the editor/storage dependency or local integration, media settings, attachment model, and migrations.
2. Add the upload route, widget configuration, validation, and tests before enabling it in post administration.
3. Enable the editor for post authoring; existing `content` values remain valid text/Markdown and require no data conversion.
4. Configure durable media storage and media delivery in each deployed environment.
5. Roll back by disabling the widget and upload route; retain existing Markdown/text content and remove the new attachment migration only through a planned database rollback.
