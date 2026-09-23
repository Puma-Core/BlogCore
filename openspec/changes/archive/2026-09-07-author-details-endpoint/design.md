## Context

El proyecto usa Django 6.1 y Django REST framework. `profiles.PublicProfile` ya contiene los ocho datos solicitados, tiene un `public_username` único y no requiere cambios de esquema. `project/app/urls.py` registra actualmente un `DefaultRouter` sin recursos y condiciona las rutas DRF al entorno de desarrollo. Ver `proposal.md` y `specs/author-details-endpoint/spec.md` para la motivación y el contrato observable.

## Goals / Non-Goals

**Goals:**

- Añadir un recurso DRF de detalle identificado por `public_username`.
- Mantener la respuesta limitada a los campos públicos definidos por el contrato.
- Integrar la ruta de forma compatible con el router y la configuración de URLs existente.
- Mantener el endpoint de autor disponible en cualquier `ENVIRONMENT`, incluyendo desarrollo y producción.
- Cubrir serialización, selección por `public_username`, acceso anónimo, 404 y el valor vacío de `photo_url`.

**Non-Goals:**

- No modificar `PublicProfile`, sus migraciones, onboarding ni el admin.
- No permitir lookup por ID, listar perfiles ni añadir filtros o paginación.
- No implementar autenticación de `Client`, validación de secretos, permisos por cliente o CORS.
- No exponer campos del usuario relacionado, redes sociales, posts u otros datos derivados.

## Decisions

### Recurso de detalle con lookup por `public_username`

Se implementará un recurso de detalle con ruta `/api/authors/<str:public_username>/`, usando el `public_username` único de `PublicProfile` como criterio. Se elige un endpoint de detalle explícito sobre un `ViewSet` con listado porque no se necesita una colección ni operaciones de escritura. El ID interno no se expondrá como parte de la ruta en esta entrega; podrá evaluarse en una ampliación futura si se requiere un segundo método de identificación.

### Serializer explícito de campos

Se usará un serializer explícito con los ocho campos públicos, en vez de serializar todos los campos del modelo. Esto evita exponer accidentalmente relaciones o atributos futuros y mantiene el contrato estable. `photo_url` conservará el valor del modelo, por lo que un campo vacío se serializará como cadena vacía.

### Vista de solo lectura y acceso anónimo

La vista será de solo lectura y usará el comportamiento GET permitido por la configuración DRF actual para recursos públicos. La búsqueda por `public_username` inexistente producirá 404 mediante la resolución estándar del recurso; no se añadirá una respuesta alternativa que pueda filtrar información sobre otros perfiles. Las operaciones distintas de GET no formarán parte de la ruta.

### Integración de rutas

El recurso se registrará dentro del `DefaultRouter` y la inclusión de sus rutas se mantendrá fuera de la condición de `ENVIRONMENT`, conservando el prefijo `/api/`. El login browsable y el schema OpenAPI seguirán siendo tooling de desarrollo; esta separación permite publicar el endpoint sin publicar esas herramientas.

### Tests sin base de datos cuando sea posible

Los tests seguirán el estilo pytest del repositorio. Cada subgrupo de implementación SHALL comenzar con sus tests unitarios correspondientes o crearlos junto con la primera implementación del subgrupo; no se permite dejar la creación de tests para una fase posterior. El serializer se probará con instancias construidas en memoria y la vista/routing con mocks o el cliente DRF según el patrón existente; se evitará persistencia salvo que sea estrictamente necesaria para verificar el lookup del ORM. El grupo final solo ejecutará verificaciones globales y no será responsable de crear tests funcionales nuevos.

## Risks / Trade-offs

- **Endpoint público expone los datos configurados como públicos** → Limitar estrictamente el serializer a ocho campos y revisar que no incluya relaciones o datos de autenticación.
- **Exposición accidental de tooling en producción** → Mantener `rest_framework.urls` y el schema OpenAPI dentro de la condición de desarrollo; solo el router de recursos públicos será común a todos los entornos.
- **Los nombres públicos también pueden ser enumerados** → El `public_username` es un dato público y único; esta entrega evita exponer el ID interno, pero no pretende resolver por sí sola la enumeración de nombres. Autenticación, rate limiting o controles adicionales quedan para un cambio posterior.
- **La autenticación de `Client` no está conectada a DRF** → Mantenerla fuera de alcance y planificarla como cambio independiente si los consumidores requieren acceso autenticado o autorización por dominio.

## Migration Plan

1. Trabajar la propuesta desde `origin/author-details-endpoint`.
2. Añadir el serializer, la vista y el registro de ruta junto con sus tests en ramas `feature/author_details_endpoint/<subgrupo>`.
3. Ejecutar `uv run python project/manage.py check` y `uv run pytest`.
4. No ejecutar migraciones: el cambio no modifica modelos ni base de datos.
5. Para revertir, eliminar el recurso, sus tests y el registro del router.
