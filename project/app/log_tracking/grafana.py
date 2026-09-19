import json
import time

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import BaseLogService
from .enums import LogLevel, LogService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Mapping

class LogDeliveryError(RuntimeError):
    """Raised when a log service cannot deliver an event."""


class GrafanaLokiService(BaseLogService):
    service = LogService.GRAFANA_LOKI

    def __init__(self) -> None:
        """Configure the Grafana Loki push endpoint.

        Returns:
            None.

        Raises:
            ImproperlyConfigured: If ``LOG_TRACKING_LOKI_BASE_URL`` is missing.
        """
        if not settings.LOG_TRACKING_LOKI_BASE_URL:
            raise ImproperlyConfigured("LOG_TRACKING_LOKI_BASE_URL must be configured.")

        self.url = f"{settings.LOG_TRACKING_LOKI_BASE_URL.rstrip('/')}/loki/api/v1/push"

    def emit(
        self,
        level: LogLevel,
        message: str,
        labels: Mapping[str, str],
        metadata: Mapping[str, str] | None = None,
    ) -> None:
        """Send a structured log event to the configured Loki endpoint.

        Args:
            level: Severity of the event.
            message: Human-readable event message.
            labels: Stable Loki stream labels for the event.
            metadata: Optional flat structured metadata for the log entry.

        Returns:
            True when Loki accepts the log event.

        Raises:
            ValueError: If ``level`` is not a ``LogLevel`` value.
            LogDeliveryError: If the HTTP request fails or Loki rejects it.
        """
        if not isinstance(level, LogLevel):
            raise ValueError("level must be a LogLevel value.")

        values: list[dict[str, str] | str] = [
            str(time.time_ns()),
            json.dumps({"level": level.value, "message": message}),
        ]
        if metadata:
            values.append(dict(metadata))

        headers = {"Content-Type": "application/json"}
        if settings.LOG_TRACKING_LOKI_TOKEN:
            headers["Authorization"] = f"Bearer {settings.LOG_TRACKING_LOKI_TOKEN}"

        payload: dict[str, Any] = {"streams": [{"stream": dict(labels), "values": [values]}]}

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as error:
            raise LogDeliveryError("Grafana Loki log delivery failed.") from error
