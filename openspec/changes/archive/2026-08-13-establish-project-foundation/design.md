## Context

See proposal.md — Why for motivation. The repository contains an already-implemented Django 6.1 project scaffold: `pyproject.toml` declares `django>=6.1` with Python `>=3.14`, dependencies are managed by `uv`, and the Django project package lives at `the_blog/` (`manage.py`, `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`). The scaffold uses stock settings: SQLite, debug on, console email backend, and only the default `django.contrib` apps registered. No custom apps exist yet. The required behavior is defined in `specs/project-foundation/spec.md`.

## Goals / Non-Goals

**Goals:**
- Record and codify the existing scaffold so future changes build on a stable, well-understood base.
- Establish a modular, app-based architecture that keeps integrations (LLM, payments, click trackers, social media) isolated and reversible.
- Keep the foundation verifiable: the spec requirements map to checks that pass on the current tree.

**Non-Goals:**
- No new features: content publishing, LLM integration, payments, tracking, and social media are future changes, not part of this one.
- No changes to runtime behavior of the existing scaffold.
- No production deployment or configuration management.

## Decisions

- **Django as the core framework** — Django ships with the batteries the blog needs (admin, auth, ORM, migrations, templates, sessions, static handling), so features can be added incrementally instead of reinventing infrastructure. *Alternative: Flask/FastAPI* — lighter, but would require assembling auth, admin, and ORM separately; Django's batteries fit a personal experimentation platform.
- **uv + Python 3.14 for dependency management** — single lockfile, fast sync, and a pinned toolchain make the environment reproducible. *Alternative: pip + requirements.txt / pipenv* — no lockfile guarantees; uv is already in place.
- **One isolated Django app per capability** — each future feature (posts, LLM tools, payments, trackers, social) becomes its own app under `INSTALLED_APPS`, exposing its own `urls.py` included from the project root. This is the concrete mechanism behind the "Extensible application architecture" requirement. *Alternative: a single monolith `blog` app* — simpler initially but makes it harder to isolate or remove experiments cleanly, which is the opposite of what an experimentation platform needs.
- **Stock settings kept as the documented development baseline** — the current `settings.py` (SQLite, debug, console email) is the default for local work. Future changes may introduce environment-driven configuration when they need production concerns; that is out of scope here.
- **Specs as the evolving project map** — the OpenSpec change documents the foundation, and each future feature will add its own delta on top, so the repository grows with the project instead of requiring big-bang rewrites.

## Risks / Trade-offs

- **Foundation drift** — if future changes bypass the modular-app pattern, the extensibility contract erodes. → Mitigation: the spec requirement is explicit and each new change adds its spec delta against `project-foundation`.
- **Premature modularity** — many isolated apps can add boilerplate early. → Mitigation: apps are created only when a capability actually lands; nothing is pre-created now.
- **Stale documentation** — documentary specs can drift from the code over time. → Mitigation: the archive step of each future change keeps specs in sync with what is actually implemented.
