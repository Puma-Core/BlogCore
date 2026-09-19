## 1. Corregir referencias del módulo Django

- [x] 1.1 Cambiar `DJANGO_SETTINGS_MODULE` de `project.settings` a `app.settings` en `project/manage.py`
- [x] 1.2 Cambiar `DJANGO_SETTINGS_MODULE` de `project.settings` a `app.settings` en `project/app/asgi.py`
- [x] 1.3 Cambiar `DJANGO_SETTINGS_MODULE` de `project.settings` a `app.settings` en `project/app/wsgi.py`
- [x] 1.4 Cambiar `ROOT_URLCONF` de `project.urls` a `app.urls` en `project/app/settings.py`
- [x] 1.5 Cambiar `WSGI_APPLICATION` de `project.wsgi.application` a `app.wsgi.application` en `project/app/settings.py`
- [x] 1.6 Actualizar docstrings de `asgi.py`, `wsgi.py`, `settings.py` y `urls.py` para reflejar el prefijo `app`
- [x] 1.7 Verificar que `python project/manage.py check` pasa sin errores

## 2. Actualizar documentación

- [x] 2.1 Actualizar `README.md` con la estructura real del proyecto (`project/` con `app/` interno)
- [x] 2.2 Corregir todos los comandos de `uv run` para que usen la ruta `project/manage.py`
- [x] 2.3 Añadir una sección que documente el historial de renombrado (`the_blog` → `project` → `project/app`) y el motivo del cambio
- [x] 2.4 Añadir sección de configuración (settings clave: SECRET_KEY, DEBUG, ALLOWED_HOSTS, base de datos)
- [x] 2.5 Revisar que el README no contenga referencias obsoletas a `the_blog` ni a `project.*` de módulos inexistentes