## Why

Los posts hoy pertenecen directamente al usuario de autenticación, por lo que no pueden aprovechar la identidad y los datos públicos ya configurados en `PublicProfile`. Asociarlos al perfil público permite que los futuros consumidores de contenido desplieguen información pública del autor sin exponer datos de la cuenta.

## What Changes

- **BREAKING** Reemplazar la relación de autor de `Post` desde el usuario de Django hacia `PublicProfile`.
- Conservar la creación y administración de posts mediante Django admin, seleccionando el perfil público como autor.
- Migrar los posts existentes hacia el perfil público correspondiente a su autor, preservando los registros que tengan una correspondencia.
- Mantener fuera de alcance las vistas, plantillas y URLs de presentación pública.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `post-model`: La autoría persistida de un post pasa a ser un perfil público para disponibilizar la información pública del autor.

## Impact

- Modelo, migración de datos y administración de `posts.Post`.
- Dependencia de `posts` sobre `profiles.PublicProfile`.
- Pruebas unitarias del modelo y del admin de posts.
