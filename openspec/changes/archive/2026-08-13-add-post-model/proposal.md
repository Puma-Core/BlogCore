## Why

La rama `add/post_app` creó la app `posts` con el modelo `Post`, pero el modelo todavía no está disponible: la migración `0001_initial` no está aplicada (`showmigrations` reporta 0 de 1 y `db.sqlite3` pesa 0 bytes) ni el modelo está registrado en el admin de Django. Este change hace que el modelo `Post` sea real y gestionable, sentando la base del bloque de publicación de contenido del proyecto.

## What Changes

- Aplicar la migración `0001_initial` de `posts` para crear la tabla `posts_post` en la base de datos SQLite.
- Registrar el modelo `Post` en `project/posts/admin.py` para que sea gestionable desde `/admin/`.
- Limpiar los archivos espurios `__init__.py` (raíz del repo y `project/`) creados durante el churn de la app.
- Sin cambios en otras capacidades ni en la configuración del proyecto (la app `posts` ya está en `INSTALLED_APPS`).

## Capabilities

### New Capabilities

- `post-model`: Persistencia y gestión del contenido `Post` (título, contenido, autor, fechas) a través del admin de Django.

### Modified Capabilities

## Impact

- Código afectado: `project/posts/models.py`, `project/posts/admin.py`, migración `project/posts/migrations/0001_initial.py`.
- Configuración: `project/app/settings.py` (ya registra `posts`, sin cambios adicionales).
- Base de datos: `db.sqlite3` (se aplican las migraciones; el archivo está ignorado por git).
- Limpieza: `__init__.py` en la raíz y en `project/`.