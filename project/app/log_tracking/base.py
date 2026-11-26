from abc import ABC, abstractmethod
from typing import Mapping

from .enums import LogLevel, LogService


class BaseLogService(ABC):
    service: LogService

    @abstractmethod
    def emit(
        self,
        level: LogLevel,
        message: str,
        labels: Mapping[str, str],
        metadata: Mapping[str, str] | None = None,
    ) -> None:
        """Deliver a structured log event to the external service."""
