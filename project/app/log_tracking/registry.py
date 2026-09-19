from collections.abc import Callable

from .base import BaseLogService
from .enums import LogService


class LogServiceRegistry:
    _instance: "LogServiceRegistry | None" = None
    services: dict[LogService, BaseLogService]

    def __new__(cls) -> "LogServiceRegistry":
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.services = {}
            cls._instance = instance
        return cls._instance

    def get_or_create(
        self,
        service: LogService,
        factory: Callable[[], BaseLogService],
    ) -> BaseLogService:
        if service not in self.services:
            self.services[service] = factory()
        return self.services[service]

    @classmethod
    def reset(cls) -> None:
        if cls._instance is not None:
            cls._instance.services.clear()
        cls._instance = None
