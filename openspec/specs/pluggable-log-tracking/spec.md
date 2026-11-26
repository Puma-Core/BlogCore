## Purpose

Provide vendor-neutral, configurable delivery of structured application logs to
external log services while making Grafana Loki available as the first provider.

## ADDED Requirements

### Requirement: Configurable log-service implementation
The system SHALL select the active log-service implementation from a configured
implementation class. Application code that emits logs MUST use the configured
service without importing a provider-specific implementation.

#### Scenario: Configured service emits a log
- **WHEN** an application component emits a log while a valid service
  implementation class is configured
- **THEN** the log is delivered through that implementation

#### Scenario: Invalid implementation is configured
- **WHEN** the configured implementation class does not satisfy the log-service
  contract
- **THEN** initialization fails with a configuration error that identifies the
  invalid implementation

### Requirement: Shared provider contract and service registry
Every supported external logging provider SHALL implement the shared log-service
contract. The system SHALL expose a single registry instance that maps each
supported service enum value to exactly one initialized service instance for the
life of the process.

#### Scenario: A service is resolved repeatedly
- **WHEN** the same supported service is requested more than once
- **THEN** the registry returns the same service instance each time

#### Scenario: A new provider is added
- **WHEN** a provider implements the shared contract and is registered for its
  service enum value
- **THEN** it can receive logs without changes to logging callers

#### Scenario: Several services are resolved
- **WHEN** callers resolve more than one registered service and resolve any of
  them again
- **THEN** each service has one distinct provider instance and repeated
  resolution does not create a duplicate instance

### Requirement: Structured log events
The system SHALL accept a log-level enum, message, labels, and optional flat
metadata for every emitted log. It MUST provide a timestamp and serialize the
event in the format required by the selected service.

#### Scenario: A log event is emitted
- **WHEN** a caller sends a log with a supported log-level enum and message
- **THEN** the selected service receives the level, message, timestamp, labels,
  and supplied flat metadata

#### Scenario: Unsupported log level is supplied
- **WHEN** a caller supplies a value outside the log-level enum
- **THEN** the system rejects the event before sending a provider request

### Requirement: Grafana Loki HTTP delivery
The Grafana Loki implementation SHALL send log events to the configured local
Loki base URL using HTTP `POST /loki/api/v1/push` and an `application/json`
body. It MUST send each entry timestamp as a string in Unix nanoseconds.

#### Scenario: Loki accepts a log event
- **WHEN** the configured local Loki server accepts a log event
- **THEN** it receives a JSON payload containing a stream label object and a
  values array with the nanosecond timestamp and serialized log message

#### Scenario: Loki rejects a log event
- **WHEN** Loki returns a non-success HTTP response or the request cannot be
  completed
- **THEN** the logging call reports a provider-delivery error with the response
  or transport context

### Requirement: Unit verification with mocked transport
The system SHALL have unit tests that verify configured service resolution,
singleton reuse, and provider delivery with the external HTTP transport mocked
so that tests do not send a real network request.

#### Scenario: A simulated Loki success response is received
- **WHEN** a unit test emits a log to the configured Loki service with a
  simulated successful HTTP response
- **THEN** it verifies the request method, endpoint, headers, and serialized
  payload without contacting a Loki server

#### Scenario: A simulated Loki failure response is received
- **WHEN** a unit test emits a log to the configured Loki service with a
  simulated HTTP or transport failure
- **THEN** it verifies the provider-delivery error without contacting a Loki
  server
