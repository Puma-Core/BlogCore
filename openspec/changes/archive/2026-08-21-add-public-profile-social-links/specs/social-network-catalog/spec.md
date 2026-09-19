## Purpose

Define configuraciones de redes sociales para construir de forma consistente los enlaces asociados a perfiles, manteniendo la lógica en modelos de Django.

## ADDED Requirements

### Requirement: Configuraciones de redes sociales con variables
El sistema SHALL permitir que los usuarios staff creen, consulten, actualicen y eliminen configuraciones de redes sociales desde la administración. Cada configuración SHALL tener un nombre único, `template_url`, `icon_url` y una o más variables asociadas. `template_url` MUST referenciar únicamente variables asociadas a esa configuración. Los usuarios que no sean staff MUST NOT poder crear ni modificar configuraciones ni sus variables asociadas.

#### Scenario: Staff registra una configuración de red social
- **WHEN** un usuario staff asocia una o más variables existentes a una configuración y guarda nombre, `template_url` e `icon_url` válidos
- **THEN** la configuración queda disponible con esos campos para crear instancias de usuario

#### Scenario: Plantilla referencia una variable no configurada
- **WHEN** un usuario staff guarda un `template_url` que referencia una variable no asociada a la configuración
- **THEN** el sistema rechaza la configuración sin modificarla

### Requirement: Instancias de redes sociales de usuario con autor inmutable
El sistema SHALL permitir que un usuario tenga una o más instancias de redes sociales. Cada instancia SHALL pertenecer a su usuario creador y a una sola configuración de red social. El autor MUST permanecer inmutable después de crear la instancia. Una instancia solo podrá asociar instancias de variables definidas por su configuración. La URL y el ícono del enlace MUST obtenerse de `template_url` e `icon_url` de la configuración y de los valores de sus variables asociadas.

#### Scenario: Usuario crea una instancia de red social configurada
- **WHEN** un usuario selecciona una configuración disponible y asocia instancias para todas sus variables requeridas
- **THEN** el sistema guarda la instancia de red y construye su URL

#### Scenario: Usuario asocia una instancia de variable no configurada
- **WHEN** un usuario intenta asociar a una instancia de red una instancia de variable que no pertenece a su configuración
- **THEN** el sistema rechaza la asociación y no modifica la instancia de red

#### Scenario: Se intenta reasignar el autor de una instancia de red
- **WHEN** cualquier usuario intenta cambiar el autor de una instancia de red social existente
- **THEN** el sistema rechaza la operación y conserva el autor original

### Requirement: Archivado de instancias de redes sociales
El autor SHALL poder archivar una instancia de red social activa que le pertenece. El sistema MUST conservar el registro archivado, MUST NOT permitir su borrado físico y MUST excluirlo de los enlaces construidos por el modelo. Una instancia archivada MUST NOT aceptar actualizaciones ni nuevas asociaciones de instancias de variables.

#### Scenario: Usuario archiva una instancia de red propia
- **WHEN** un usuario archiva una instancia de red social activa que le pertenece
- **THEN** el sistema conserva el registro como archivado y el modelo deja de construir su URL

## OUT OF SCOPE

- Vistas, plantillas o URLs propias del proyecto para exponer los enlaces públicamente.
- Dashboard de gestión de instancias de redes sociales.
