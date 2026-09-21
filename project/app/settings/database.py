import os
from pathlib import Path

from app.settings.errors import MissingDatabaseVariableError, UnsupportedDatabaseEngineError

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite").lower()
BASE_DIR = Path(__file__).resolve().parents[2]


def _required_postgresql_value(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise MissingDatabaseVariableError.for_name(name)
    return value


if DATABASE_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif DATABASE_ENGINE in {"postgres", "postgresql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _required_postgresql_value("DATABASE_NAME"),
            "USER": _required_postgresql_value("DATABASE_USER"),
            "PASSWORD": _required_postgresql_value("DATABASE_PASSWORD"),
            "HOST": _required_postgresql_value("DATABASE_HOST"),
            "PORT": os.getenv("DATABASE_PORT", "5432"),
        }
    }
else:
    raise UnsupportedDatabaseEngineError()
