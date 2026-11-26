## 1. Verify Toolchain

- [x] 1.1 Confirm the active Python version is 3.14 (`uv run python --version` reports 3.14.x)
- [x] 1.2 Confirm Django 6.1 is installed in the environment (`uv run python -c "import django; print(django.get_version())"` reports 6.1.x)
- [x] 1.3 Confirm `pyproject.toml` declares Python `>=3.14` and `django>=6.1` and that `uv sync` completes cleanly

## 2. Verify Django Project Structure

- [x] 2.1 Confirm the `the_blog/` project package contains `manage.py`, `settings.py`, `urls.py`, `wsgi.py`, and `asgi.py`
- [x] 2.2 Run `python manage.py check` from `the_blog/` and confirm no system errors are reported
- [x] 2.3 Start the development server and confirm it boots without errors

## 3. Verify Admin and Development Defaults

- [x] 3.1 Confirm `django.contrib.admin` is in `INSTALLED_APPS` and `/admin/` is routed in `urls.py`
- [x] 3.2 Visit `/admin/` on a running server and confirm the login page is served
- [x] 3.3 Confirm `settings.py` uses SQLite as the default database, has `DEBUG = True`, the console email backend, and `STATIC_URL = 'static/'`

## 4. Repository Hygiene

- [x] 4.1 Add `db.sqlite3` to `.gitignore` so the local database is not tracked
- [x] 4.2 Replace the placeholder `pyproject.toml` description with a short description of the project (personal experiment blog built with Django)
- [x] 4.3 Populate `README.md` with the project's purpose, the tech stack, and how to run it locally (`uv sync`, `python manage.py runserver`)
