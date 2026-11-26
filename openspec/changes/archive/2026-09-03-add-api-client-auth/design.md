## Context

El proyecto es un blog Django 6.1 con las apps `posts` y `profiles` ya establecidas. No existe hoy un mecanismo para identificar o autorizar consumidores externos por dominio. Ver `proposal.md` para la motivación del cambio y `specs/api-client-auth/spec.md` para los requisitos de comportamiento.

## Goals / Non-Goals

**Goals:**
- Crear la app `clients` con el modelo `Client` que almacene nombre, dominios permitidos, secreto, estado activo, grupos, permisos y timestamps.
- Generar un secreto único automáticamente cuando no se provee uno.
- Validar el campo `domain` como una lista de URLs con protocolo separadas por coma.
- Implementar un admin de Django que muestre el secreto solo en los formularios de creación/edición y no en el changelist ni en vistas readonly.
- Proveer helpers en el modelo para consultar permisos de Django y validar dominios de request.
- Cubrir el modelo, validadores y admin con tests unitarios.

**Non-Goals:**
- Integración con Django REST framework en esta entrega.
- Endpoints HTTP de autenticación o autorización.
- Cifrado del secreto en base de datos (se trata como texto sensible mediante control de visibilidad).
- Sincronización de permisos con usuarios de Django.

## Decisions

### Separate `clients` app

Se creará una nueva aplicación Django `clients` en `project/clients/` en lugar de extender `profiles`. Esto mantiene la responsabilidad de autenticación de clientes API separada del perfil público de usuarios humanos y facilita futuras extensiones hacia DRF.

### Use Django's built-in `Group` and `Permission` models

El modelo `Client` tendrá dos relaciones `ManyToMany` directas a `auth.Group` y `auth.Permission` en lugar de heredar `PermissionsMixin`. `PermissionsMixin` está diseñado para modelos de usuario y asume campos como `is_superuser`; usarlo en un modelo no-usuario generaría confusión y campos no deseados. Las relaciones directas permiten reutilizar el sistema de permisos de Django sin esa sobrecarga.

### Plain-text secret with admin-side visibility control

El secreto se almacenará como texto plano en la base de datos. No se implementa cifrado en esta entrega porque el alcance se limita a controlar quién puede verlo. La protección se realiza en el admin: el campo se renderiza en el formulario de creación/edición pero se excluye del changelist y de los campos readonly. Si en el futuro se requiere cifrado, el cambio será transparente para el contrato del modelo.

### URL-based domain validation

El campo `domain` se validará con `urllib.parse` o `django.core.validators.URLValidator` por cada entrada separada por coma. Se exige protocolo (`http://` o `https://`) y un hostname no vacío. Esto garantiza que la comparación contra el `Host` de un request sea predecible.

### Auto-generate secret in model `save()` and admin form

Para cumplir el requisito de que todo cliente tenga un secreto no vacío, se generará automáticamente en `save()` si el campo está vacío. Adicionalmente, el formulario del admin generará y mostrará el secreto antes del submit para que el operador pueda copiarlo. El generador usará `secrets.token_urlsafe()` para obtener tokens aleatorios de longitud fija.

### Test with pytest

Los tests se escribirán como funciones de pytest. Los validadores y metadatos del modelo se probarán sin base de datos. Los escenarios que requieren persistencia, permisos o el admin form usarán `@pytest.mark.django_db` de `pytest-django`, evitando la suite `django.test.TestCase` y el comando `manage.py test`. Esto mantiene el estilo del resto del proyecto (`project/tests/unit_test/`).

### Domain matching by hostname

El helper `is_domain_allowed(host)` comparará el hostname recibido contra los hostnames extraídos del campo `domain`. No se compararán protocolos ni paths, ya que el requisito se centra en el origen del request.

## Risks / Trade-offs

- **[Secreto en texto plano]** → Mitigación: el alcance actual limita la exposición al admin. Futuras iteraciones pueden agregar hash o cifrado.
- **[Generación de secreto en `save()` oculta el valor al operador]** → Mitigación: el formulario del admin genera y muestra el secreto antes del primer guardado.
- **[Validación de dominio por URL requiere protocolo]** → Mitigación: se documenta en el help_text del campo y en los mensajes de error.
- **[Relaciones ManyToMany a Permission/Group no integran `has_perm` nativo]** → Mitigación: se implementan métodos explícitos `has_perm` y `has_module_perms` en el modelo.

## Migration Plan

1. Crear la app `clients`, el modelo `Client` y su migración inicial.
2. Registrar `clients` en `INSTALLED_APPS`.
3. Implementar el admin y los validadores.
4. Ejecutar `uv run python project/manage.py makemigrations` y `uv run python project/manage.py migrate`.
5. Ejecutar `uv run pytest` y `uv run python project/manage.py check`.
6. Si es necesario revertir, eliminar la app de `INSTALLED_APPS` y revertir la migración inicial.
