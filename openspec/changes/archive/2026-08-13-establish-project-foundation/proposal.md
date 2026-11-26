## Why

This is a personal blog used as an experimentation platform: a place to try out different features and publish posts about what is discovered and worth sharing. The base Django project scaffold is already implemented (Django 6.1 on Python 3.14, managed with uv). This change is **documentary and preparatory**: it records the current state of the project and establishes the architectural contract that will keep it flexible as features are added over time — from LLM integrations and payment methods to click trackers and social media. Specifying the foundation now gives every future change a stable base to build on.

## What Changes

- Documents the already-implemented base scaffold: repository layout, tooling (`uv`, Python 3.14, Django 6.1), and the Django project package (`the_blog/`).
- Establishes project conventions that future changes must follow (modular Django apps, environment-aware settings, dependency management via `uv`).
- Defines the extensibility principles that guarantee integrations (LLM, payments, click trackers, social media, and anything else) can be added as isolated apps without touching core behavior.
- Sets the groundwork for the core content-publishing capability (authoring and publishing personal posts) which will be built in a dedicated future change.
- No runtime behavior changes in this change — it is documentary and preparatory by design.

## Capabilities

### New Capabilities

- `project-foundation`: The base Django project scaffold, its tooling, and the modularity/extensibility contract that ensures future capabilities (content publishing, LLM, payments, tracking, social media) can be added as isolated Django apps without changing the core.

### Modified Capabilities

## Impact

- **Code**: The existing Django project package `the_blog/` (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`) and `manage.py`.
- **Tooling**: `uv` for dependency management, Python 3.14, Django 6.1, SQLite default database.
- **Specs**: A new `project-foundation` spec documents what the system must provide and becomes the reference for all future changes.
- **No breaking changes**: Nothing is modified, removed, or replaced.
