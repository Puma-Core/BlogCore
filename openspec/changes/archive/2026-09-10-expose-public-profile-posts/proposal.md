## Why

Los consumidores públicos pueden consultar los datos de un autor, pero no pueden descubrir ni obtener sus artículos mediante una URL estable. Los posts necesitan un identificador legible derivado del título y acotado al autor para permitir enlaces simples sin depender del ID interno ni generar colisiones entre autores.

## What Changes

- Agregar un identificador tipo slug/`unique_name` calculado desde el título del post, normalizado con palabras separadas por `-`.
- Garantizar en la base de datos que el `unique_name` no se repita para el mismo autor y conservar la identidad del post cuando se consulte por autor y slug.
- Exponer una API pública de solo lectura para listar los posts de un perfil mediante `public_username`, mostrando el título, un extracto del contenido de máximo 256 caracteres, la fecha de publicación y el nombre completo del autor.
- Permitir obtener un artículo individual mediante el `public_username` del autor y su `unique_name`, mostrando el contenido completo además del título, la fecha, el autor y el identificador legible.
- Devolver 404 para perfiles, slugs o combinaciones autor-artículo inexistentes, sin usar el ID interno como criterio alternativo.
- Cubrir modelo, serialización, endpoints, routing, generación de identificadores y restricciones de unicidad con tests unitarios.

## Capabilities

### New Capabilities

- `public-profile-posts-endpoint`: Consulta pública de la colección de posts de un perfil y de un post individual por `public_username` y `unique_name`.

### Modified Capabilities

- `post-model`: Añadir el identificador legible derivado del título y su unicidad por autor como parte del contrato de persistencia de posts.

## Impact

- `project/posts/models.py` y una nueva migración para el campo derivado y la restricción de base de datos.
- Nuevos serializers, vistas y rutas DRF bajo `/api/` para posts públicos.
- Tests bajo `project/tests/unit_test/posts/` y posiblemente builders compartidos.
- Las respuestas expondrán únicamente los datos públicos del post y su autor necesarios para el contrato; el listado usará una representación resumida y el detalle incluirá el contenido completo. No se modificarán autenticación, onboarding ni el endpoint existente de detalles de autor.
- Se requerirán representaciones o serializers diferenciados para evitar exponer el contenido completo en el listado y garantizar el límite de 256 caracteres.
- Los títulos que produzcan el mismo slug para un mismo autor requerirán una decisión explícita de conflicto durante creación o actualización, en lugar de duplicar silenciosamente el identificador.
