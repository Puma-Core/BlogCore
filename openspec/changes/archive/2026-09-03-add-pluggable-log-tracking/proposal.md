## Why

The application needs to send operational logs to different external services
without coupling calling code to Grafana, CloudWatch, Google Cloud Logging, or
their transport protocols. The first destination is a local Grafana Loki
server, while the design must make later providers straightforward to add.

## What Changes

- Add a vendor-neutral logging module selected through a configured
  implementation class rather than direct provider references.
- Define a shared base contract for all log-service implementations and enums
  for supported services and log levels.
- Add a service registry singleton that maps each service enum to its service
  singleton.
- Implement the Grafana Loki adapter for a local server using the Loki HTTP
  `POST /loki/api/v1/push` JSON endpoint.
- Send structured log messages with the timestamp, level, message, labels, and
  optional flat metadata required by the selected provider API.

## Capabilities

### New Capabilities
- `pluggable-log-tracking`: Configurable, structured delivery of application
  logs through interchangeable external logging services.

### Modified Capabilities

- None.

## Impact

- New logging module, provider base class, service and level enums, singleton
  registry, Grafana Loki HTTP adapter, configuration, and tests.
- Django settings will provide the selected implementation class and local Loki
  connection settings.
- No database schema or user-facing API change is expected; an HTTP client
  dependency may be added if the project has no suitable installed client.
- Add `pytest-mock` as a development dependency for unit tests that mock the
  external HTTP transport.
