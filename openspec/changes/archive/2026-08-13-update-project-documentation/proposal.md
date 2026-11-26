## Why

La estructura del proyecto cambió: el paquete Django se renombró de `the_blog` a `project/app`, pero la documentación y las referencias internas quedaron desactualizadas (`the_blog/*` en README y `project.*` en settings, que apuntan a un módulo que ya no existe). Esto rompe la puesta en marcha con `No module named 'project'` y deja el proyecto sin documentar correctamente.

## What Changes

- Corregir las referencias internas del proyecto Django para que apunten al módulo `app.*` (`DJANGO_SETTINGS_MODULE`, `ROOT_URLCONF`, `WSGI_APPLICATION`).
- Actualizar `README.md` con la estructura real del proyecto (`project/app/`), los comandos de `uv run` correctos y documentación de configuración.
- Documentar el historial de renombrado (de `the_blog` a `project/app`) para que cualquier desarrollador entienda la estructura actual.
- Asegurar que `python project/manage.py check` pase sin errores tras la corrección.

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- Código afectado: `project/manage.py`, `project/app/settings.py`, `project/app/urls.py`, `project/app/asgi.py`, `project/app/wsgi.py`.
- Documentación afectada: `README.md`.
- Sin cambios en dependencias ni esquema de base de datos.
