# postgresql-database

## Purpose

Proveer una configuración PostgreSQL reproducible para Django, con conexión configurable por entorno y SQLite como backend predeterminado.

## Requirements

### Requirement: Configurable database connection
La aplicación SHALL conservar SQLite como backend por defecto y SHALL aceptar mediante variables de entorno el backend, host, puerto, nombre de base de datos, usuario, contraseña y opciones equivalentes para una conexión PostgreSQL.

#### Scenario: Default application configuration
- **WHEN** la aplicación se inicia sin variables de configuración de base de datos
- **THEN** Django usa SQLite y conserva `project/db.sqlite3` como base de datos local

#### Scenario: PostgreSQL connection settings
- **WHEN** se selecciona PostgreSQL y se proporcionan sus variables de conexión
- **THEN** Django construye `DATABASES["default"]` con esos valores sin requerir cambios en el código

### Requirement: Centralized database settings
La configuración de la base de datos SHALL residir en `project/app/settings/database.py`, y el módulo principal de settings SHALL importar desde allí la definición de `DATABASES`.

#### Scenario: Database settings module
- **WHEN** Django carga la configuración del proyecto
- **THEN** la selección del backend y la extracción de variables de entorno se resuelven desde `settings/database.py`

### Requirement: SQLite default and explicit selection
La aplicación SHALL usar SQLite cuando no se selecciona otro backend y SHALL permitir seleccionar SQLite explícitamente mediante una variable de configuración documentada.

#### Scenario: Local SQLite execution
- **WHEN** un desarrollador no proporciona configuración de base de datos o selecciona SQLite
- **THEN** Django usa el archivo SQLite configurado y la aplicación sigue pudiendo ejecutar sus comandos de gestión

### Requirement: PostgreSQL dependency
El proyecto SHALL declarar un driver compatible con la versión soportada de PostgreSQL y SHALL incluirlo en el lockfile.

#### Scenario: Clean dependency installation
- **WHEN** un desarrollador ejecuta `uv sync` desde un checkout limpio
- **THEN** el driver PostgreSQL está instalado y Django puede cargar el backend PostgreSQL

### Requirement: External PostgreSQL connection
La aplicación SHALL conectarse a una instancia PostgreSQL externa cuando el backend PostgreSQL y sus variables de conexión estén configurados. Docker Compose SHALL pasar esta configuración al servicio Django, pero SHALL NOT provisionar, ejecutar ni almacenar una instancia PostgreSQL propia.

#### Scenario: Container startup with external database
- **WHEN** un desarrollador ejecuta `docker compose up --build` con las variables de conexión PostgreSQL configuradas
- **THEN** Django usa el host externo configurado, aplica las migraciones contra esa instancia y sirve la aplicación

#### Scenario: Database isolation
- **WHEN** se inspecciona la configuración de Docker Compose
- **THEN** no existe ningún servicio, volumen ni healthcheck destinado a ejecutar PostgreSQL dentro del proyecto

### Requirement: Database configuration validation
La configuración SHALL fallar con un mensaje accionable durante la carga de settings cuando se selecciona PostgreSQL sin las variables obligatorias, y SHALL usar SQLite únicamente cuando el backend no se haya seleccionado explícitamente.

#### Scenario: Missing required configuration
- **WHEN** se selecciona PostgreSQL y falta una credencial o parámetro obligatorio
- **THEN** la carga de settings identifica la configuración incompleta y explica qué variable debe definirse
