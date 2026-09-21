## Context

Actualmente `project/app/settings.py` define SQLite directamente y `docker-compose.yml` solo levanta la aplicación. El proyecto ya usa `uv`, tiene un arranque Docker con migraciones y mantiene un volumen para `.venv`; PostgreSQL debe integrarse mediante variables de entorno sin cambiar los modelos ni las rutas. SQLite debe seguir siendo el valor predeterminado para conservar los flujos locales existentes, y las pruebas unitarias deben seguir siendo ejecutables sin depender de un daemon externo.

## Goals / Non-Goals

**Goals:**

- Permitir que Django use PostgreSQL con una configuración clara y totalmente parametrizable.
- Mantener SQLite como backend predeterminado cuando no hay configuración de base de datos.
- Centralizar la selección del backend y la extracción de variables en `project/app/settings/database.py`.
- Conectar Django desde Compose a una instancia PostgreSQL externa configurada por variables de entorno.
- Evitar que el contenedor Django o Compose provisionen o almacenen PostgreSQL.
- Documentar la operación diaria y la aplicación de migraciones Django sobre la base seleccionada.
- Cubrir la selección de backend, los valores de conexión y los errores de configuración con pruebas.

**Non-Goals:**

- No eliminar soporte explícito para SQLite ni reescribir modelos o migraciones de Django.
- No incluir backups programados, replicación, tuning de producción, TLS ni alta disponibilidad.
- No imponer una instancia PostgreSQL en los tests unitarios que no necesitan persistencia.

## Decisions

### Backend seleccionado mediante variable explícita

Introducir una variable como `DATABASE_ENGINE` con SQLite como valor predeterminado y PostgreSQL como alternativa explícita. La configuración PostgreSQL usará variables separadas para nombre, usuario, contraseña, host y puerto, con valores seguros para Compose. Cuando PostgreSQL se seleccione explícitamente y falte una variable obligatoria, la configuración fallará de forma accionable en lugar de cambiar silenciosamente a SQLite.

### Módulo dedicado de configuración

Convertir la configuración actual en un paquete `settings` y ubicar la lógica de base de datos en `project/app/settings/database.py`. El módulo principal importará `DATABASES` desde allí, mientras que `database.py` será responsable de leer y validar las variables de entorno. La reorganización no cambiará los valores predeterminados de SQLite ni los puntos de entrada de Django.

### Driver psycopg

Usar `psycopg` como driver de PostgreSQL y fijar su dependencia en el proyecto mediante `uv`. Se prefiere la distribución binaria del paquete para evitar requisitos de compilación innecesarios en el contenedor de desarrollo, manteniendo una versión compatible con Python 3.14 y Django soportado.

### PostgreSQL externo a Compose

No se añadirá ningún servicio `db` a Compose. El servicio `app` recibirá mediante variables de entorno el backend, host, puerto, nombre, usuario y contraseña de una instancia PostgreSQL administrada fuera de este repositorio. El arranque podrá reintentar la conexión antes de migrar, pero no incluirá healthcheck, volumen ni `depends_on` para PostgreSQL. Sin esas variables, la aplicación seguirá usando SQLite.

### Migraciones como operación de arranque

El arranque aplicará `manage.py migrate` contra el backend seleccionado. No se incluirán operaciones de exportación, importación o transferencia de datos como parte de este cambio.

### Tests desacoplados del servidor

Las pruebas de settings verificarán la construcción de ambas configuraciones con variables aisladas. Las pruebas que requieran consultas PostgreSQL se marcarán como integración y usarán la conexión configurada por el entorno de CI; la suite unitaria seguirá sin requerir un servicio externo.

## Risks / Trade-offs

- [La instancia PostgreSQL externa no está disponible] -> Reintentos de conexión antes de migrar y documentación para revisar la conectividad y los logs del proveedor externo.
- [La contraseña o configuración de conexión se expone accidentalmente] -> Usar valores de desarrollo solo como defaults, documentar secretos fuera del repositorio y no añadir credenciales reales.
- [Los tests locales no tienen PostgreSQL] -> Mantener pruebas de configuración sin ORM y separar explícitamente las pruebas de integración.

## Migration Plan

1. Convertir `settings.py` en un paquete de configuración y extraer la lógica de base de datos a `settings/database.py`.
2. Añadir el driver, la configuración parametrizable y las pruebas de selección de backend, conservando SQLite como valor predeterminado.
3. Añadir al servicio Django las variables que permiten seleccionar una instancia PostgreSQL externa; no añadir un servicio de base de datos a Compose.
4. Actualizar el arranque y la documentación; ejecutar migraciones sobre el backend seleccionado.
5. Revertir eliminando la configuración PostgreSQL del entorno y seleccionando SQLite sin modificar la instancia externa ni borrar `db.sqlite3`.
