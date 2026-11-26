from app.settings import get_env_bool, get_env_list, get_env_value, get_optional_env_value
from django.conf import settings


def test_allowed_hosts_default_to_local_addresses():
    assert settings.ALLOWED_HOSTS[:2] == ["localhost", "127.0.0.1"]


def test_wsgi_static_files_are_collected_and_served():
    assert settings.STATIC_ROOT.name == "staticfiles"
    assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE


def test_environment_list_uses_configured_hosts(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "blog.example.test, 192.0.2.10 ")

    assert get_env_list("ALLOWED_HOSTS", ("localhost", "127.0.0.1")) == [
        "blog.example.test",
        "192.0.2.10",
    ]


def test_csrf_trusted_origins_use_configured_or_default_values(monkeypatch):
    monkeypatch.delenv("CSRF_TRUSTED_ORIGINS", raising=False)
    assert get_env_list("CSRF_TRUSTED_ORIGINS", ("http://localhost",)) == [
        "http://localhost"
    ]

    monkeypatch.setenv(
        "CSRF_TRUSTED_ORIGINS", "https://blog.example.test, https://admin.example.test"
    )
    assert get_env_list("CSRF_TRUSTED_ORIGINS", ("http://localhost",)) == [
        "https://blog.example.test",
        "https://admin.example.test",
    ]


def test_runtime_values_use_environment_over_defaults(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "container-secret")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("ENVIRONMENT", "container")
    monkeypatch.setenv("API_BASE_URL", "https://api.example.test")

    assert get_env_value("SECRET_KEY", "default-secret") == "container-secret"
    assert not get_env_bool("DEBUG", True)
    assert get_env_value("ENVIRONMENT", "development") == "container"
    assert get_env_value("API_BASE_URL", "http://localhost:8000") == "https://api.example.test"


def test_optional_runtime_value_treats_an_empty_environment_variable_as_unset(monkeypatch):
    monkeypatch.setenv("AWS_S3_ADDRESSING_STYLE", "")

    assert get_optional_env_value("AWS_S3_ADDRESSING_STYLE") is None
