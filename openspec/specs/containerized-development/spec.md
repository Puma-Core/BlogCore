# containerized-development

## Purpose

Provide a reproducible container-based development environment that runs the Django project without relying on a host package manager or host Python environment.

## Requirements

### Requirement: Self-contained development image
The project SHALL provide a development container image based on Alpine Linux that includes Git, Python 3.14, and uv. The image SHALL install project dependencies from the repository's declared dependency metadata without requiring Python, uv, or a package manager on the host.

#### Scenario: Build on a host without Python tooling
- **WHEN** a developer builds the development service with Docker Compose on a host that has Docker but no Python, uv, or project package manager installed
- **THEN** the image build completes with the tooling and dependencies required to run the Django project

### Requirement: Isolated container virtual environment
The development service SHALL keep its Python virtual environment in container-managed storage that is not bind-mounted from the host project directory.

#### Scenario: Dependency synchronization
- **WHEN** the development service synchronizes project dependencies
- **THEN** the resulting virtual environment is available to processes in the container and is absent from the host working tree

### Requirement: Bidirectional source synchronization
The development service SHALL bind-mount the current project directory so changes made on the host are immediately available in the container and changes made in the container are persisted on the host.

#### Scenario: Host source edit
- **WHEN** a developer changes an application source file on the host while the service is running
- **THEN** the container uses the updated file without rebuilding the image

#### Scenario: Container source edit
- **WHEN** a developer changes an application source file from within the container
- **THEN** the updated file is visible in the host working directory

### Requirement: Published WSGI application server
The Docker Compose development service SHALL serve the Django WSGI application bound to all container network interfaces and publish its configured HTTP port to the host.

#### Scenario: Dashboard access from the host
- **WHEN** the development service is running
- **THEN** a browser on the host can reach the Django administrative dashboard through the published port

#### Scenario: API access from an external client
- **WHEN** the development service is running and an external client uses an allowed host name or address
- **THEN** the client can reach the project's API endpoints through the published port

### Requirement: Runtime environment injection
The Docker Compose development service SHALL pass the Django secret key, debug mode, environment name, permitted hosts, and API base URL from environment variables to the WSGI application.

#### Scenario: Configured service startup
- **WHEN** a developer supplies runtime environment variables to Docker Compose
- **THEN** the WSGI application starts with those values available to its Django settings
