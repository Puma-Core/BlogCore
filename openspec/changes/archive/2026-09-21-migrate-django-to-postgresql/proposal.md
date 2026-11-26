## Why

El proyecto usa SQLite como base de datos por defecto. Aunque ese valor debe conservarse para no romper los flujos locales existentes, sus limitaciones de concurrencia, escalabilidad y funcionalidades hacen necesario que Django también pueda conectarse a PostgreSQL mediante variables de entorno.

## What Changes

- Añadir el driver de PostgreSQL y configurar Django para construir `DATABASES` desde variables de entorno.
- Extraer la configuración de base de datos a `project/app/settings/database.py` para mantenerla separada del resto de los settings.
- Configurar Docker Compose para que Django seleccione una instancia PostgreSQL externa mediante variables de entorno, sin provisionar la base de datos en Compose.
- Mantener SQLite como configuración predeterminada cuando no se proporcionan variables de base de datos.
- Documentar las variables de conexión, el arranque de Django, la disponibilidad de la instancia externa y los comandos de migración.
- Fallar de forma visible cuando PostgreSQL sea seleccionado con una configuración incompleta, sin cambiar silenciosamente a SQLite.
- Añadir pruebas de configuración y validación de la conexión PostgreSQL sin acoplar la suite unitaria a un servidor externo.

## Capabilities

### New Capabilities

- `postgresql-database`: Configuración, ejecución y operación de Django sobre PostgreSQL.

### Modified Capabilities

- `project-foundation`: SQLite permanece como base de datos predeterminada y PostgreSQL queda disponible mediante configuración explícita por variables de entorno.
- `containerized-development`: El entorno Compose debe pasar a Django la configuración de una instancia PostgreSQL externa, sin iniciar ni almacenar una base de datos propia.

## Impact

- Afecta a `project/app/settings.py`, `project/app/settings/database.py`, `pyproject.toml` y `uv.lock`.
- Modifica `docker-compose.yml`, el arranque del contenedor y la documentación de desarrollo para usar una instancia externa.
- Añade configuración y pruebas para variables de base de datos y disponibilidad de la conexión externa.
- No modifica los modelos ni los contratos HTTP existentes.
- No elimina el archivo SQLite existente, no cambia el backend por defecto ni incluye transferencia de datos entre SQLite y PostgreSQL.
