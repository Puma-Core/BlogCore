## 1. Logging Contracts and Configuration

- [x] 1.1 Add `pytest-mock` as a test dependency and configure the `mocker` fixture for the logging tests.
- [x] 1.2 Write unit tests for configured implementation resolution and invalid configuration before implementing the logging contract.
- [x] 1.3 Create the logging module with `LogService` and `LogLevel` enums and the abstract base service contract.
- [x] 1.4 Add Django settings that read the selected implementation class and Loki connection values from environment variables; validate that the configured class satisfies the contract.

## 2. Singleton Infrastructure

- [x] 2.1 Write unit tests proving repeated resolution reuses one provider per registered service and multiple services do not duplicate instances.
- [x] 2.2 Implement the log-service registry singleton that maps service enums to provider instances and reuses them.
- [x] 2.3 Add a test-only registry reset or injection seam so unit tests remain isolated.

## 3. Grafana Loki Provider

- [x] 3.1 Write unit tests with `mocker.patch` for the configured Loki provider using mocked HTTP success, rejection, and transport-failure responses; assert the complete outbound request and prevent network access.
- [x] 3.2 Implement the Grafana Loki service using the base contract and `requests` directly.
- [x] 3.3 Serialize level, message, labels, flat metadata, and a string Unix-nanosecond timestamp into the Loki `POST /loki/api/v1/push` JSON payload.

## 4. Verification

- [x] 4.1 Run focused logging tests and `uv run python project/manage.py check`.
- [x] 4.2 Verify the unit test suite covers mocked successful, rejected, and transport-failure responses without allowing outbound network requests.
