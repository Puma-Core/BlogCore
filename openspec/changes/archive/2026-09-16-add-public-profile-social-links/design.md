## Context

`SocialNetworkInstance` ya pertenece a un usuario, contiene las instancias de variables que resuelven su URL y puede archivarse. `PublicProfile` tiene una relación uno a uno con ese mismo usuario, pero no conserva qué instancias deben presentarse públicamente. Véanse `proposal.md` y los deltas de especificación para la motivación y el comportamiento requerido.

## Goals / Non-Goals

**Goals:**

- Mantener una selección explícita y ordenable de instancias de redes sociales por perfil público.
- Validar que la selección solo incluya instancias activas del usuario propietario del perfil.
- Consultar desde el perfil únicamente enlaces actualmente utilizables, sin duplicar la resolución de URL, ícono o variables.

**Non-Goals:**

- Crear endpoints, formularios o interfaz de administración para gestionar la selección.
- Cambiar las reglas de creación, propiedad o archivado de redes sociales y sus variables.
- Reparar automáticamente relaciones históricas inválidas, pues la relación es nueva.

## Decisions

### Usar un modelo de asociación explícito

Se creará un modelo de asociación entre `PublicProfile` y `SocialNetworkInstance`, con una restricción de unicidad para el par. El modelo permite concentrar la validación de pertenencia y ofrece un lugar para añadir atributos de presentación futuros, como orden, sin rediseñar la relación. Una relación many-to-many implícita no permite encapsular esta validación ni extender el vínculo de forma segura.

### Validar propiedad y estado al crear o modificar la asociación

El modelo de asociación verificará que el usuario del perfil coincida con el autor de la instancia y que esta no esté archivada. De este modo, las asociaciones inválidas se rechazan en el límite del dominio. Solo filtrar al consultar se descartó porque conservaría relaciones inválidas y permitiría que otro usuario las agregara.

### Exponer una consulta de enlaces activos desde el perfil

El perfil ofrecerá sus instancias de redes sociales seleccionadas mediante una consulta que excluya instancias archivadas. La URL y el ícono seguirán siendo propiedades de `SocialNetworkInstance`, para mantener una única fuente de resolución basada en la configuración y las variables. Copiar esos datos al vínculo se descartó porque se desincronizarían al actualizar una variable o configuración.

## Risks / Trade-offs

- [Una instancia seleccionada se archiva después de asociarse] -> La consulta del perfil la excluye automáticamente; la asociación se conserva como historial.
- [Las validaciones de modelos no se ejecutan al usar operaciones masivas del ORM] -> Los flujos de escritura deberán usar la ruta de validación del modelo; las pruebas cubrirán la validación y la consulta pública.
- [Una consulta del perfil requiere cargar relaciones adicionales] -> Usar `select_related` o `prefetch_related` en consumidores que necesiten configuración y variables para evitar consultas N+1.

## Migration Plan

1. Agregar el modelo de asociación y la relación desde el perfil, junto con la restricción de unicidad y la migración de Django.
2. Desplegar sin migración de datos: los perfiles existentes comenzarán sin redes seleccionadas.
3. Si se necesita revertir antes de crear asociaciones, eliminar la migración revierte el esquema. Después de que existan relaciones, respaldarlas antes de una reversión para evitar pérdida de selecciones.
