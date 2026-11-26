from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import BaseLogService
from .enums import LogService
from .registry import LogServiceRegistry


def get_configured_service() -> BaseLogService:
    class_path = settings.LOG_TRACKING_SERVICE_CLASS
    if not class_path:
        raise ImproperlyConfigured("LOG_TRACKING_SERVICE_CLASS must be configured.")

    module_name, _, class_name = class_path.rpartition(".")
    if not module_name:
        raise ImproperlyConfigured("LOG_TRACKING_SERVICE_CLASS must be a dotted path.")

    service_class = getattr(import_module(module_name), class_name)
    if not isinstance(service_class, type) or not issubclass(service_class, BaseLogService):
        raise ImproperlyConfigured(
            "LOG_TRACKING_SERVICE_CLASS must inherit from BaseLogService."
        )

    service = getattr(service_class, "service", None)
    if not isinstance(service, LogService):
        raise ImproperlyConfigured(
            "LOG_TRACKING_SERVICE_CLASS must declare a LogService value."
        )

    return LogServiceRegistry().get_or_create(service, service_class)
