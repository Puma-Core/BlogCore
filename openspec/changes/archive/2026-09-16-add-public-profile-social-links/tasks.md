## 1. Modelo y migración

- [x] 1.1 Crear el modelo de asociación entre perfil público e instancia de red social, con relaciones, restricción de unicidad y validaciones de propietario y estado activo; verificar sus pruebas unitarias de validación.
- [x] 1.2 Exponer desde `PublicProfile` la consulta de instancias sociales seleccionadas y activas; verificar que devuelve enlaces propios y excluye los archivados.
- [x] 1.3 Generar y aplicar la migración de Django para la nueva asociación; verificar que `uv run python project/manage.py migrate` finaliza correctamente.

## 2. Pruebas y verificación

- [x] 2.1 Agregar pruebas unitarias para asociación válida, duplicada, de otro propietario y archivada; verificar que `uv run pytest project/tests/unit_test/profiles` pasa.
- [x] 2.2 Agregar pruebas para la consulta de redes sociales del perfil y la resolución de URL e ícono mediante la instancia existente; verificar que cubren inclusión y exclusión requeridas.
- [x] 2.3 Ejecutar las comprobaciones finales de Django y la suite completa; verificar que `uv run python project/manage.py check` y `uv run pytest` pasan.
