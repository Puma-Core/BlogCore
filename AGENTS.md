# Repository Guide

## Project

- Requires Python 3.14+ and `uv`; run `uv sync` from the repository root.
- Run Django commands from the root as `uv run python project/manage.py <command>`. The settings module is `app.settings`, while the package is `project/app`; do not invoke `django-admin` from the root.
- The default database is the ignored SQLite file `project/db.sqlite3`. For model changes, run `uv run python project/manage.py makemigrations` followed by `uv run python project/manage.py migrate`.
- Project configuration is in `project/app`; domain apps are `project/posts`, `project/profiles`, and `project/clients`. API routes are registered in `project/app/urls.py`.

## Tests

- Pytest uses `DJANGO_SETTINGS_MODULE=app.settings`, adds `project` to `PYTHONPATH`, and uses importlib mode from `pyproject.toml`; test files named `test_*.py` are discovered recursively under the repository test root.
- Organize unit tests by application under `project/tests/unit_test/<app>/`, keeping each test next to the behavior it covers.
- Put serializer tests in `project/tests/unit_test/<app>/serializer/` and name them after the serializer or model, such as `test_public_profile.py`. Create this subdirectory only for an application that has a `serializers.py` module.
- Put shared test builders in `project/tests/unit_test/functions/`, reusable fixtures in `project/tests/unit_test/fixtures/`, and application-specific mocks in `project/tests/unit_test/mocks/<app>/`.
- Prefer database-free pytest tests: build model instances in memory and mock ORM managers or `Model.save`; use `@pytest.mark.django_db` only when persistence is required.
- Run all tests with `uv run pytest`, one application with `uv run pytest project/tests/unit_test/profiles`, one subfolder with `uv run pytest project/tests/unit_test/profiles/serializer`, or one file by passing its path. Use `uv run pytest -k <expression>` for selection by name.
- Before handing off Django changes, run `uv run python project/manage.py check` and the relevant tests; run the full suite for cross-application changes.

## OpenSpec

- Feature work uses the `spec-driven` workflow configured in `openspec/config.yaml`. Keep proposal, design, delta specs, and `tasks.md` together under `openspec/changes/`.
- Include unit-test work in the implementation subgroup that introduces the behavior; do not defer tests to a final phase.
- Validate archived changes with `openspec validate --archived --strict`.
- Before archiving a completed change, merge delta specs into `openspec/specs/<capability>/spec.md`; archived changes belong under `openspec/changes/archive/`.
- Put real scope decisions in `design.md` under Non-Goals; do not add generic tooling unless requested.
