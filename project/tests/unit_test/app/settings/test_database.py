import importlib

import pytest
from app.settings import database
from app.settings.errors import (
    MissingDatabaseVariableError,
    UnsupportedDatabaseEngineError,
)


def test_database_settings_default_to_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_ENGINE", raising=False)

    settings = importlib.reload(database)

    assert settings.DATABASES == {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": settings.BASE_DIR / "db.sqlite3",
        }
    }


def test_database_settings_use_postgresql_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_ENGINE", "postgresql")
    monkeypatch.setenv("DATABASE_NAME", "blog")
    monkeypatch.setenv("DATABASE_USER", "blog-user")
    monkeypatch.setenv("DATABASE_PASSWORD", "secret")
    monkeypatch.setenv("DATABASE_HOST", "database.example.test")
    monkeypatch.setenv("DATABASE_PORT", "5433")

    settings = importlib.reload(database)

    assert settings.DATABASES["default"] == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "blog",
        "USER": "blog-user",
        "PASSWORD": "secret",
        "HOST": "database.example.test",
        "PORT": "5433",
    }


def test_postgresql_configuration_does_not_fallback_to_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_ENGINE", "postgresql")
    monkeypatch.delenv("DATABASE_NAME", raising=False)
    monkeypatch.setenv("DATABASE_USER", "blog-user")
    monkeypatch.setenv("DATABASE_PASSWORD", "secret")
    monkeypatch.setenv("DATABASE_HOST", "database.example.test")

    with pytest.raises(
        MissingDatabaseVariableError,
        match="DATABASE_NAME must be set when DATABASE_ENGINE=postgresql",
    ):
        importlib.reload(database)


def test_invalid_database_engine_raises_custom_configuration_error(monkeypatch):
    monkeypatch.setenv("DATABASE_ENGINE", "mysql")

    with pytest.raises(
        UnsupportedDatabaseEngineError,
        match="DATABASE_ENGINE must be either 'sqlite' or 'postgresql'",
    ):
        importlib.reload(database)
