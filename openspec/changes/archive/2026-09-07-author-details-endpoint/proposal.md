## Why

Los consumidores externos no tienen actualmente un recurso DRF para consultar los datos públicos de un autor. El modelo `PublicProfile` ya concentra la identidad pública y sus campos, por lo que necesitamos exponer una lectura estable basada en `public_username`, evitando exponer el ID interno como identificador principal del recurso.

## What Changes

- Agregar un endpoint DRF de solo lectura para consultar un `PublicProfile` por su `public_username`.
- Devolver `public_username`, `first_name`, `last_name`, `title`, `subtitle`, `specialty`, `short_description` y `photo_url` en la respuesta JSON.
- Devolver una respuesta HTTP 404 cuando el `public_username` no corresponda a un perfil público.
- Integrar la ruta en el enrutamiento de la API y cubrir serializer, vista, routing y respuestas principales con tests unitarios.
- Mantener el endpoint disponible sin depender de `ENVIRONMENT`, tanto en desarrollo como en producción.
- Crear y ejecutar los tests unitarios desde el inicio de cada grupo de implementación; queda prohibido postergar la creación de tests para una fase final.
- Mantener la consulta por ID como una posible ampliación futura, fuera del alcance de esta entrega.
- Mantener el modelo, el onboarding, el admin y la autenticación específica de clientes API sin cambios de comportamiento.

## Capabilities

### New Capabilities

- `author-details-endpoint`: Consulta HTTP de los datos públicos de un autor mediante su `public_username`.

### Modified Capabilities

- Ninguna.

## Impact

- Nuevos módulos DRF para serializer, vista y routing del recurso de autor.
- Nuevos tests bajo `project/tests/unit_test/` y posible actualización del registro de URLs de `project/app`.
- El endpoint reutiliza `profiles.PublicProfile` y sus validaciones existentes; no requiere migración de base de datos.
- El endpoint se diseña como lectura pública de los datos ya marcados como públicos. No implementa en este cambio autenticación de `Client`, validación de secretos, autorización por permisos ni consulta por ID.
- La propuesta se gestiona en `origin/author-details-endpoint`; cada grupo de implementación se desarrollará en una rama `feature/author_details_endpoint/<subgrupo>`.
