from enum import StrEnum


class LogService(StrEnum):
    GRAFANA_LOKI = "grafana_loki"
    CLOUDWATCH = "cloudwatch"
    GOOGLE_CLOUD_LOGGING = "google_cloud_logging"


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
