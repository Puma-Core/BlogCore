# my_blog

Proyecto de blog construido con **Django 6.1** y gestionado con **uv**.

## Requisitos

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)
- Docker con Docker Compose (para ejecutar el entorno aislado)

## Instalación

```bash
# Crear el entorno virtual e instalar dependencias
uv sync
```

> **Nota:** se recomienda usar `uv run` en lugar de activar el entorno virtual manualmente: es mucho más rápido y no requiere activar nada.

## Puesta en marcha

```bash
# Aplicar migraciones
uv run python project/manage.py migrate

# Arrancar el servidor de desarrollo
uv run python project/manage.py runserver
```

El servidor estará disponible en <http://127.0.0.1:8000/>.

## Docker Compose

El entorno en contenedor no requiere Python, uv ni un gestor de paquetes en el host.
La imagen Alpine incluye Git, Python y uv; Django se sirve mediante `runserver`.
El entrypoint sincroniza dependencias, aplica migraciones y recopila los archivos
estaticos antes de ejecutar el comando del contenedor. El codigo se monta desde el
directorio actual y el entorno virtual `.venv` vive en un volumen
interno de Docker, por lo que no se comparte con el host.

La secuencia de preparacion se define en `docker/start.sh` y se ejecuta como
`ENTRYPOINT`; el `CMD` de la imagen ejecuta `uv run python project/manage.py runserver
0.0.0.0:${DJANGO_PORT}`.

```bash
# Opcional: personalizar las variables de ejecución
cp .env.example .env

# Construir y arrancar el servicio WSGI
docker compose up --build
```

El panel está disponible en <http://localhost:8000/admin/> y las APIs bajo
<http://localhost:8000/api/>. Para permitir una IP o dominio externo, define
`ALLOWED_HOSTS` con valores separados por comas y expón el puerto Docker según las
políticas de red del host.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `SECRET_KEY` | clave de desarrollo | Clave secreta de Django; reemplazar fuera del desarrollo. |
| `DEBUG` | `False` | Activa o desactiva el modo debug. |
| `ENVIRONMENT` | `development` | Entorno usado por la aplicación. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos, separados por comas. |
| `API_BASE_URL` | `http://localhost:8000` | URL base expuesta en el esquema OpenAPI. |
| `DJANGO_PORT` | `8000` | Puerto donde Django escucha y que Docker publica en el host. |
| `DATABASE_ENGINE` | `sqlite` | Backend de Django. Usa `postgresql` para conectar una instancia externa. |
| `DATABASE_NAME` | sin valor | Nombre de la base PostgreSQL externa. Obligatorio con `DATABASE_ENGINE=postgresql`. |
| `DATABASE_USER` | sin valor | Usuario PostgreSQL externo. Obligatorio con `DATABASE_ENGINE=postgresql`. |
| `DATABASE_PASSWORD` | sin valor | Contraseña PostgreSQL externa. Obligatoria con `DATABASE_ENGINE=postgresql`. |
| `DATABASE_HOST` | sin valor | Host PostgreSQL externo. Obligatorio con `DATABASE_ENGINE=postgresql`. |
| `DATABASE_PORT` | `5432` | Puerto PostgreSQL externo. |

SQLite continúa siendo el backend predeterminado cuando `DATABASE_ENGINE` no está definido.
Para usar PostgreSQL, configura todas las variables requeridas en `.env` y asegúrate de que
la instancia externa sea accesible desde el host o el contenedor Django. Compose no crea,
almacena ni administra un servidor PostgreSQL.

Si `DATABASE_ENGINE=postgresql` y falta una variable obligatoria, Django falla durante la
carga de settings con un error visible; nunca cambia silenciosamente a SQLite. El arranque
reintenta las migraciones cuando la instancia externa todavía no acepta conexiones.

La configuración de base de datos está centralizada en `project/app/settings/database.py`.
Este cambio solo aplica las migraciones Django al backend seleccionado; no incluye exportación
ni importación de datos entre SQLite y PostgreSQL.

Para detener el servicio, usa `docker compose down`. Para eliminar también el entorno
virtual interno, usa `docker compose down --volumes`.

Comandos habituales durante el desarrollo:

```bash
# Seguir los registros del servidor
docker compose logs --follow app

# Ejecutar comandos de Django en el contenedor en marcha
docker compose exec app uv run python project/manage.py createsuperuser
docker compose exec app uv run python project/manage.py makemigrations

# Reconstruir despues de cambiar pyproject.toml o uv.lock
docker compose up --build
```

## Estructura del proyecto

```
my_blog/
├── project/              # Proyecto Django
│   ├── manage.py
│   └── app/              # Configuración del proyecto (paquete interno)
│       ├── settings.py
│       ├── urls.py
│       ├── asgi.py
│       └── wsgi.py
├── pyproject.toml         # Dependencias y metadatos (uv)
├── uv.lock
└── main.py                # Punto de entrada alternativo (demo)
```

## Configuración

Las opciones principales viven en `project/app/settings.py`:

| Clave           | Valor por defecto      | Descripción                                                        |
|-----------------|------------------------|--------------------------------------------------------------------|
| `SECRET_KEY`    | `django-insecure-...`  | Clave secreta. **Debe cambiarse en producción.**                   |
| `DEBUG`         | `True`                 | Modo debug. **Debe ser `False` en producción.**                    |
| `ALLOWED_HOSTS` | `[]`                   | Hosts permitidos. Añadir los dominios de despliegue en producción. |
| `DATABASES`     | SQLite (`db.sqlite3`)  | Base de datos por defecto.                                         |

## Media de posts

El editor de posts guarda Markdown en `Post.content` y puede subir imágenes a
`/api/attachments/upload/` para insertarlas como URLs en ese Markdown. El endpoint
requiere una sesión autenticada, acepta únicamente `image/jpeg` (`.jpg` y `.jpeg`)
e `image/webp`, y limita cada archivo a 5 MiB de forma predeterminada.

En desarrollo, los archivos se guardan localmente bajo `project/media/` y se sirven
desde `/media/`. Los siguientes ajustes admiten variables de entorno:

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `MEDIA_URL` | `/media/` | URL pública usada al generar referencias de adjuntos. |
| `MEDIA_ROOT` | `project/media/` | Directorio local para el backend de desarrollo. |
| `MEDIA_STORAGE_BACKEND` | `django.core.files.storage.FileSystemStorage` | Backend de Django que persiste los adjuntos. |
| `POST_ATTACHMENT_MAX_SIZE` | `5242880` | Tamaño máximo de carga en bytes. |

Para un servicio compatible con S3, configure
`MEDIA_STORAGE_BACKEND=storages.backends.s3boto3.S3Boto3Storage` y las siguientes variables
estándar de `django-storages`.
Las credenciales explícitas son opcionales: si se omiten, `boto3` usa su cadena de
credenciales ambiental (por ejemplo, un rol de instancia o variables estándar de AWS).

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `AWS_STORAGE_BUCKET_NAME` | sin valor | Bucket obligatorio para el backend S3. |
| `AWS_ACCESS_KEY_ID` | sin valor | Credencial de acceso opcional; use un gestor de secretos. |
| `AWS_SECRET_ACCESS_KEY` | sin valor | Credencial secreta opcional; nunca la incluya en el repositorio. |
| `AWS_S3_REGION_NAME` | sin valor | Región que usa el cliente S3. |
| `AWS_S3_ENDPOINT_URL` | sin valor | Endpoint para un proveedor compatible con S3. |
| `AWS_S3_ADDRESSING_STYLE` | sin valor | Use `path` para forzar el formato de endpoint compatible de R2. |

Los demás ajustes de S3 usan los valores predeterminados de `django-storages`.

El bucket se valida al iniciar la aplicación cuando se selecciona el backend S3;
una configuración incompleta no cambia silenciosamente al directorio local. La
aplicación usa la abstracción `Storage` de Django, por lo que `Attachment.file` y
otros `FileField` conservan la misma interfaz local o remota.

Los adjuntos pertenecen a quien los sube y no tienen una relación de base de datos
con un post. Una imagen puede quedar sin referencia si se abandona un borrador; se
conserva como adjunto del autor y su limpieza es una política operativa futura, no
un proceso automático.

## Scripts útiles

```bash
# Crear un superusuario para el admin
uv run python project/manage.py createsuperuser

# Ejecutar checks del proyecto
uv run python project/manage.py check
```

## Historial de renombrado

El paquete del proyecto Django cambió de nombre a lo largo del tiempo. Esto explica
por qué la estructura puede no coincidir con la que generaría `django-admin startproject`:

| Etapa            | Ubicación original            | Ubicación actual   |
|------------------|-------------------------------|--------------------|
| Inicial          | `the_blog/the_blog/`          | —                  |
| Renombrado #1    | `project/the_blog/`           | —                  |
| Renombrado #2    | `project/project/`            | —                  |
| Actual           | `project/app/`                | `project/app/`     |

El motivo del cambio fue simplificar y unificar los nombres de la estructura. Tras el
último renombrado, las referencias internas del módulo apuntan a `app.*`
(`DJANGO_SETTINGS_MODULE = 'app.settings'`, `ROOT_URLCONF = 'app.urls'`,
`WSGI_APPLICATION = 'app.wsgi.application'`).

> **Importante:** si se renombra de nuevo el paquete interno, hay que actualizar
> `DJANGO_SETTINGS_MODULE` en `manage.py`, `asgi.py` y `wsgi.py`, además de
> `ROOT_URLCONF` y `WSGI_APPLICATION` en `settings.py`.

## Estado actual

- Proyecto Django recién inicializado (solo configuración base).
- Admin de Django disponible en `/admin/`.
- Sin aplicaciones propias todavía.
