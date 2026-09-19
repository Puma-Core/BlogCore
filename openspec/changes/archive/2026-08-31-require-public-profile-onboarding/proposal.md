## Why

Un usuario de Django admin sin `PublicProfile` no puede completar su identidad pública ni debe acceder a las herramientas administrativas antes de hacerlo. El flujo debe crear el perfil desde la sesión autenticada y liberar las herramientas sólo cuando un administrador asigne manualmente los grupos correspondientes.

## What Changes

- Unificar el flujo de onboarding y las herramientas en el admin estándar de Django bajo `/admin/`; eliminar el panel separado `/dashboard/`.
- Restringir a los usuarios staff sin perfil público a un grupo de onboarding con acceso únicamente al formulario de creación de su propio perfil, además del cierre de sesión.
- Redirigir desde cualquier herramienta administrativa al formulario de creación mientras el usuario staff no tenga perfil público.
- Mantener los permisos de herramientas en grupos de Django que un administrador asigna manualmente después de que el usuario complete su perfil.
- Conservar el formulario público asociado exclusivamente al usuario autenticado de la sesión, sin selector de usuario ni posibilidad de cambiar esa asociación.
- Actualizar el alcance de `PublicProfile` para incluir el flujo web de alta y la inmutabilidad de su usuario autenticado asociado.

## Capabilities

### New Capabilities

- `public-profile-onboarding`: Flujo de Django admin para crear el perfil público pendiente y controlar las herramientas disponibles mediante grupos y permisos.

### Modified Capabilities

- `public-user-profile`: El perfil público se crea mediante el flujo de onboarding para el usuario autenticado y su asociación de usuario no puede modificarse.

## Impact

- Configuración del admin estándar, sus grupos y permisos de onboarding, su formulario de `PublicProfile`, su override de template limitado y sus controles de acceso por propietario.
- Guard de acceso para herramientas de `/admin/` y eliminación de la ruta `/dashboard/`.
- Modelo y pruebas de `profiles.PublicProfile`, grupos de Django y flujos admin para usuarios staff y superusuarios.
