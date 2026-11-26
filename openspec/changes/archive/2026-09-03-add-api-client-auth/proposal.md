## Why

El blog no tiene hoy una forma de identificar y autorizar a consumidores externos (aplicaciones, integraciones o frontales separados) que quieran acceder a ciertos recursos por dominio. Necesitamos un modelo de clientes que gestione un secreto único y permisos de Django, administrable desde el panel de administración.

## What Changes

- Crear una nueva aplicación Django `clients` dentro de `project/`.
- Agregar el modelo `Client` con los campos `name`, `domain`, `secret`, `is_active`, `groups`, `permissions`, `created_at` y `updated_at`.
- Generar un `secret` único automáticamente al crear un cliente.
- Ocultar el `secret` en el admin de Django después de guardado; mostrarlo únicamente durante la creación o edición para que el operador pueda copiarlo.
- Validar que el campo `domain` contenga una o más URLs válidas separadas por coma, incluyendo protocolo.
- Exponer métodos helper en el modelo para consultar permisos (`has_perm`, `has_module_perms`) y validar si un dominio de request está permitido.
- Agregar tests unitarios para el modelo, los validadores y la configuración del admin.

## Capabilities

### New Capabilities

- `api-client-auth`: Gestión de clientes API con secreto único, dominios permitidos, permisos/grupos de Django y administración desde Django admin.

### Modified Capabilities

Ninguna.

## Impact

- Nueva app `project/clients/` con modelo, admin, validadores, migraciones y tests.
- Registro de `clients` en `INSTALLED_APPS` de `project/app/settings.py`.
- No impacta modelos existentes de `posts` ni `profiles`.
