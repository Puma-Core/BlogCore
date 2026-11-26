## 1. feature/author_details_endpoint/api-contract

- [x] 1.1 Escribir primero los tests unitarios del serializer para exigir únicamente `public_username`, `first_name`, `last_name`, `title`, `subtitle`, `specialty`, `short_description` y `photo_url`; implementar el serializer y verificar que los tests pasen sin exponer campos adicionales.
- [x] 1.2 Escribir primero los tests unitarios de la vista para el lookup exclusivo por `public_username` y la respuesta HTTP 200; implementar la vista DRF de detalle de solo lectura y verificar que los tests pasen.
- [x] 1.3 Escribir primero el test unitario de routing para `/api/authors/<public_username>/`; registrar la vista en el router y verificar que el recurso se resuelva con el prefijo `/api/` existente.
- [x] 1.4 Preparar los builders o mocks reutilizables que necesiten los tests del endpoint siguiendo las convenciones de `project/tests/unit_test/`, y verificar que puedan ejecutarse sin migraciones nuevas.

## 2. feature/author_details_endpoint/read-behavior

- [x] 2.1 Escribir primero el test unitario de acceso GET anónimo; ajustar la implementación necesaria y verificar que un perfil existente devuelva los ocho campos públicos.
- [x] 2.2 Escribir primero el test unitario de `public_username` inexistente; ajustar la resolución de la vista y verificar HTTP 404 sin datos de otro perfil.
- [x] 2.3 Escribir primero el test unitario para username vacío o malformado; ajustar el routing o validación necesaria y verificar HTTP 404 sin criterio alternativo.
- [x] 2.4 Escribir primero el test unitario para `photo_url` vacío; ajustar la serialización si fuera necesario y verificar que la respuesta conserve una cadena vacía.
- [x] 2.5 Escribir primero los tests unitarios de rechazo de lookup por ID, operaciones de escritura y listado; ajustar la exposición del endpoint y verificar que solo exista la consulta GET por `public_username`.

## 3. feature/author_details_endpoint/integration-quality

- [x] 3.1 Ejecutar `uv run python project/manage.py check` después de que los subgrupos anteriores tengan sus tests y corregir cualquier problema global de configuración, importación o routing.
- [x] 3.2 Ejecutar `uv run pytest` y verificar que la suite completa pase junto con todos los tests creados dentro de los subgrupos anteriores.
- [x] 3.3 Confirmar que no se generen cambios de modelo o migraciones, documentar la propuesta en `origin/author-details-endpoint` y mantener la autenticación de `Client` fuera de este cambio.
- [x] 3.4 Escribir primero tests de routing para `ENVIRONMENT=development` y `ENVIRONMENT=production`; ajustar la inclusión del router para que el endpoint esté disponible en ambos entornos sin publicar el login browsable ni el schema OpenAPI en producción.
