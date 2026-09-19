## Purpose

Ofrecer a consumidores públicos una forma estable de descubrir y consultar los artículos publicados por un perfil mediante su nombre público y un identificador legible del artículo.

## ADDED Requirements

### Requirement: Consulta pública de posts por perfil

El sistema SHALL exponer un recurso HTTP de solo lectura para listar los posts asociados a un `PublicProfile` identificado por su `public_username`. Cada elemento SHALL incluir únicamente `unique_name`, `title`, `content_preview`, `created_at` y `author_full_name`. `content_preview` SHALL contener como máximo los primeros 256 caracteres del contenido y el sistema MUST limitar ese valor durante la consulta de datos, sin cargar el contenido completo para recortarlo durante la serialización.

#### Scenario: Se listan los posts de un perfil existente

- **WHEN** un consumidor anónimo realiza una petición GET a `/api/authors/<public_username>/posts/` para un perfil existente
- **THEN** el sistema responde HTTP 200 con la colección de posts de ese perfil y cada elemento contiene el contrato público definido

#### Scenario: El listado limita el contenido en la consulta

- **WHEN** un post tiene contenido de más de 256 caracteres y un consumidor solicita la colección de su autor
- **THEN** la respuesta incluye únicamente los primeros 256 caracteres como `content_preview` y el contenido completo no se carga para construir ese campo

#### Scenario: El perfil consultado no existe

- **WHEN** un consumidor realiza una petición GET a `/api/authors/<public_username>/posts/` con un nombre público inexistente
- **THEN** el sistema responde HTTP 404 y no devuelve posts de otro perfil

#### Scenario: La colección no expone posts de otros autores

- **WHEN** un perfil tiene posts y otros perfiles también tienen posts
- **THEN** la colección del primer perfil contiene únicamente posts cuyo autor sea ese `public_username`

### Requirement: Consulta de un post por identificador legible

El sistema SHALL exponer un recurso HTTP de solo lectura para obtener un post mediante la combinación de `public_username` y `unique_name`. La combinación SHALL identificar como máximo un post; el ID interno del post no SHALL ser un criterio alternativo de búsqueda. La respuesta SHALL incluir `unique_name`, `title`, `content` completo, `created_at`, `updated_at`, `public_username` y `author_full_name`.

#### Scenario: Se consulta un post existente

- **WHEN** un consumidor anónimo realiza una petición GET a `/api/authors/<public_username>/posts/<unique_name>/` con una combinación existente
- **THEN** el sistema responde HTTP 200 con el post correspondiente, incluido su `content` completo

#### Scenario: El identificador pertenece a otro autor

- **WHEN** un consumidor solicita un `unique_name` existente bajo el `public_username` de otro perfil
- **THEN** el sistema responde HTTP 404 y no devuelve el post encontrado bajo el autor incorrecto

#### Scenario: El post no existe

- **WHEN** un consumidor solicita un `unique_name` que no corresponde a un post del perfil
- **THEN** el sistema responde HTTP 404 sin usar el ID interno ni otro criterio alternativo

### Requirement: Acceso público de solo lectura

Los recursos de posts SHALL permitir GET sin sesión autenticada y SHALL rechazar operaciones de escritura o listados que no estén definidos por las rutas públicas del contrato.

#### Scenario: Cliente anónimo consulta posts

- **WHEN** un consumidor sin sesión solicita una colección o un post existente
- **THEN** el sistema responde correctamente sin exigir autenticación

#### Scenario: No se permite modificar desde el recurso público

- **WHEN** un consumidor intenta crear, actualizar o eliminar un post mediante las rutas públicas
- **THEN** el sistema rechaza la operación y no modifica los datos
