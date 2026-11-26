## Purpose

Ofrecer a consumidores externos una consulta estable y de solo lectura de los datos públicos de un autor, identificando el perfil mediante su `public_username` y sin exponer el ID interno como identificador principal.

## ADDED Requirements

### Requirement: Consulta de detalles públicos por nombre público

El sistema SHALL exponer un recurso HTTP de solo lectura para consultar un autor mediante su `public_username`. Una consulta válida SHALL devolver únicamente los campos públicos `public_username`, `first_name`, `last_name`, `title`, `subtitle`, `specialty`, `short_description` y `photo_url`.

#### Scenario: Se consulta un perfil existente por nombre público

- **WHEN** un consumidor realiza una petición GET a `/api/authors/<public_username>/` con el `public_username` de un `PublicProfile` existente
- **THEN** el sistema responde HTTP 200 con un objeto JSON que contiene exactamente los ocho campos públicos definidos

#### Scenario: Se consulta un perfil inexistente

- **WHEN** un consumidor realiza una petición GET con un `public_username` que no corresponde a un `PublicProfile`
- **THEN** el sistema responde HTTP 404 y no devuelve datos de otro perfil

#### Scenario: Se consulta usando un nombre público no válido

- **WHEN** un consumidor realiza una petición GET con un valor vacío, malformado o no válido para el `public_username`
- **THEN** el sistema responde HTTP 404 y no ejecuta una consulta de perfil con un criterio alternativo

### Requirement: Acceso de lectura y selección por nombre público

El recurso SHALL permitir la consulta GET sin exigir una sesión de usuario autenticada. El recurso SHALL seleccionar perfiles únicamente por `public_username`; el ID interno no SHALL ser un criterio de búsqueda en esta entrega.

#### Scenario: Cliente anónimo consulta un perfil

- **WHEN** un consumidor sin sesión realiza una petición GET al `public_username` de un perfil existente
- **THEN** el sistema responde HTTP 200 con los datos públicos del perfil

#### Scenario: No se permite buscar por ID interno

- **WHEN** un consumidor intenta consultar el recurso usando el ID interno del perfil
- **THEN** el sistema no trata ese valor como criterio alternativo de búsqueda en esta entrega

### Requirement: Disponibilidad independiente del entorno

El endpoint de detalles públicos SHALL estar disponible bajo `/api/` sin depender del valor de `ENVIRONMENT`, tanto en desarrollo como en producción. La disponibilidad del endpoint no SHALL implicar que el login browsable o el schema OpenAPI deban publicarse fuera del entorno de desarrollo.

#### Scenario: Endpoint disponible en producción

- **WHEN** la aplicación se ejecuta con `ENVIRONMENT=production` y un consumidor solicita un `public_username` existente
- **THEN** el sistema resuelve el endpoint y responde con los datos públicos del autor

#### Scenario: Endpoint disponible en desarrollo

- **WHEN** la aplicación se ejecuta con `ENVIRONMENT=development` y un consumidor solicita un `public_username` existente
- **THEN** el sistema resuelve el mismo endpoint bajo `/api/`

### Requirement: Tratamiento de campos opcionales

El sistema SHALL representar `photo_url` con el valor almacenado en el perfil, incluyendo una cadena vacía cuando el perfil no tenga una URL de foto configurada, sin reemplazarla por una URL generada o por datos privados del usuario.

#### Scenario: Perfil sin foto configurada

- **WHEN** se consulta un `PublicProfile` existente cuyo `photo_url` está vacío
- **THEN** la respuesta HTTP 200 incluye `photo_url` como cadena vacía
