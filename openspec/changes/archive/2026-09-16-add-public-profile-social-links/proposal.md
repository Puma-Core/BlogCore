## Why

Las instancias de redes sociales y sus variables ya existen, pero un perfil público no puede seleccionar ni relacionar las que deben mostrarse. Es necesario que cada perfil público pueda componer sus enlaces sociales a partir de las instancias ya configuradas por su propietario.

## What Changes

- Agregar una relación entre `PublicProfile` e instancias de redes sociales para seleccionar múltiples redes que se mostrarán en el perfil.
- Restringir la relación a instancias activas cuyo autor sea el usuario propietario del perfil.
- Exponer desde el modelo del perfil las redes sociales seleccionadas, preservando los datos de configuración, variables, URL e ícono de cada instancia.
- Evitar que una misma instancia de red social se agregue más de una vez al mismo perfil.

## Capabilities

### New Capabilities

- `public-profile-social-links`: Asociación y consulta de enlaces de redes sociales seleccionados por un perfil público.

### Modified Capabilities

- `public-user-profile`: El perfil público incluye redes sociales instanciadas seleccionadas por su propietario.

## Impact

- Afecta `project/profiles/models.py` y sus migraciones de Django.
- Requiere pruebas unitarias del modelo y de sus validaciones en `project/tests/unit_test/profiles/`.
- No agrega endpoints, vistas ni dependencias externas.
