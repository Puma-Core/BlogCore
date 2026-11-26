## 1. Aplicar migraciones

- [x] 1.1 Ejecutar `uv run python project/manage.py migrate` y confirmar que la migración `posts.0001_initial` se aplica
- [x] 1.2 Verificar con `uv run python project/manage.py showmigrations posts` que `0001_initial` quede marcada como aplicada `[X]`
- [x] 1.3 Confirmar que `db.sqlite3` deja de pesar 0 bytes tras la migración

## 2. Registrar Post en el admin

- [x] 2.1 Registrar el modelo `Post` en `project/posts/admin.py` (importar y registrar con `admin.site.register` o decorador)
- [x] 2.2 Añadir `list_display` básico al modelo admin de `Post` (al menos `title` y `created_at`)
- [x] 2.3 Ejecutar `uv run python project/manage.py check` y confirmar que no hay errores del sistema

## 3. Limpieza y verificación final

- [x] 3.1 Eliminar `__init__.py` de la raíz del repo y de `project/`
- [x] 3.2 Ejecutar de nuevo `uv run python project/manage.py check` para confirmar que la limpieza no rompe nada
- [x] 3.3 Confirmar que el admin queda operativo: el modelo `Post` aparece en `/admin/` (verificable con un superusuario si ya existe, o documentando que se requiera `createsuperuser`)