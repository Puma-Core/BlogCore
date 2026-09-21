import os
from pathlib import Path
from typing import Self

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite").lower()
BASE_DIR = Path(__file__).resolve().parents[2]


class DatabaseConfigurationError(RuntimeError):
    MISSING_VARIABLE_MESSAGE = (
        "{name} must be set when DATABASE_ENGINE=postgresql"
    )
    INVALID_ENGINE_MESSAGE = (
        "DATABASE_ENGINE must be either 'sqlite' or 'postgresql'"
    )

    @classmethod
    def missing_variable(cls, name: str) -> Self:
        return cls(cls.MISSING_VARIABLE_MESSAGE.format(name=name))

    @classmethod
    def invalid_engine(cls) -> Self:
        return cls(cls.INVALID_ENGINE_MESSAGE)


def _required_postgresql_value(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise DatabaseConfigurationError.missing_variable(name)
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
    raise DatabaseConfigurationError.invalid_engine()
