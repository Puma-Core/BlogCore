import os
from importlib import reload

import django
import pytest
import requests
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from app.log_tracking.enums import LogLevel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pytest_mock import MockFixture


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.log_tracking import (
    BaseLogService,
    GrafanaLokiService,
    LogLevel,
    LogDeliveryError,
    LogService,
    LogServiceRegistry,
    get_configured_service,
)
import app.settings as app_settings


class FakeLokiService(BaseLogService):
    service = LogService.GRAFANA_LOKI

    def emit(
            self,
            level: LogLevel,message: str, labels: Mapping[str, str], metadata:Mapping[str, str] | None = None):
        return None


class FakeCloudWatchService(BaseLogService):
    service = LogService.CLOUDWATCH

    def emit(
            self,
            level: LogLevel,message: str, labels: Mapping[str, str], metadata:Mapping[str, str] | None = None):
        return None


@pytest.fixture(autouse=True)
def reset_singletons():
    LogServiceRegistry.reset()
    yield
    LogServiceRegistry.reset()


def test_configured_service_is_validated_and_reused():
    class_path = f"{__name__}.FakeLokiService"

    with override_settings(LOG_TRACKING_SERVICE_CLASS=class_path):
        assert get_configured_service() is get_configured_service()


def test_invalid_configured_service_is_rejected():
    with override_settings(LOG_TRACKING_SERVICE_CLASS="app.log_tracking.registry.LogServiceRegistry"):
        with pytest.raises(ImproperlyConfigured, match="BaseLogService"):
            get_configured_service()


def test_registry_keeps_one_distinct_service_per_log_service():
    registry = LogServiceRegistry()

    loki = registry.get_or_create(LogService.GRAFANA_LOKI, FakeLokiService)
    cloudwatch = registry.get_or_create(LogService.CLOUDWATCH, FakeCloudWatchService)

    assert registry.get_or_create(LogService.GRAFANA_LOKI, FakeLokiService) is loki
    assert registry.get_or_create(LogService.CLOUDWATCH, FakeCloudWatchService) is cloudwatch
    assert loki is not cloudwatch


def test_registry_reset_discards_registered_services():
    registry = LogServiceRegistry()
    registry.get_or_create(LogService.GRAFANA_LOKI, FakeLokiService)

    LogServiceRegistry.reset()

    assert LogServiceRegistry() is not registry


def test_log_levels_are_limited_to_the_enum():
    assert LogLevel.INFO == "info"


def test_loki_configuration_uses_environment_variables(mocker: MockFixture):
    mocker.patch.dict(
        os.environ,
        {
            "LOG_TRACKING_LOKI_BASE_URL": "https://logs.example.test",
            "LOG_TRACKING_LOKI_TOKEN": "test-token",
        },
        clear=False,
    )

    reload(app_settings)

    assert app_settings.LOG_TRACKING_LOKI_BASE_URL == "https://logs.example.test"
    assert app_settings.LOG_TRACKING_LOKI_TOKEN == "test-token"


def test_loki_service_sends_structured_payload(mocker: MockFixture):
    post = mocker.patch("app.log_tracking.grafana.requests.post")
    with override_settings(
        LOG_TRACKING_LOKI_BASE_URL="https://logs.example.test/",
        LOG_TRACKING_LOKI_TOKEN="token",
    ):
        GrafanaLokiService().emit(
            LogLevel.INFO,
            "application started",
            {"app": "blog"},
            {"trace_id": "abc"},
        )

    url, = post.call_args.args
    request = post.call_args.kwargs
    timestamp, line, metadata = request["json"]["streams"][0]["values"][0]

    assert url == "https://logs.example.test/loki/api/v1/push"
    assert request["headers"] == {
        "Content-Type": "application/json",
        "Authorization": "Bearer token",
    }
    assert request["timeout"] == 10
    assert request["json"]["streams"][0]["stream"] == {"app": "blog"}
    assert timestamp.isdigit()
    assert line == '{"level": "info", "message": "application started"}'
    assert metadata == {"trace_id": "abc"}


def test_loki_service_surfaces_http_rejection(mocker: MockFixture):
    post = mocker.patch("app.log_tracking.grafana.requests.post")
    post.return_value.raise_for_status.side_effect = requests.HTTPError("rejected")

    with override_settings(LOG_TRACKING_LOKI_BASE_URL="https://logs.example.test"):
        with pytest.raises(LogDeliveryError, match="Grafana Loki"):
            GrafanaLokiService().emit(LogLevel.ERROR, "failed", {"app": "blog"})


def test_loki_service_surfaces_transport_failure(mocker: MockFixture):
    post = mocker.patch(
        "app.log_tracking.grafana.requests.post",
        side_effect=requests.ConnectionError("unreachable"),
    )

    with override_settings(LOG_TRACKING_LOKI_BASE_URL="https://logs.example.test"):
        with pytest.raises(LogDeliveryError, match="Grafana Loki"):
            GrafanaLokiService().emit(LogLevel.ERROR, "failed", {"app": "blog"})

    post.assert_called_once()


def test_loki_service_rejects_an_invalid_log_level(mocker: MockFixture):
    post = mocker.patch("app.log_tracking.grafana.requests.post")

    with override_settings(LOG_TRACKING_LOKI_BASE_URL="https://logs.example.test"):
        with pytest.raises(ValueError, match="LogLevel"):
            GrafanaLokiService().emit(
                "invalid",  # type: ignore[arg-type]
                "invalid",
                {"app": "blog"},
            )

    post.assert_not_called()
