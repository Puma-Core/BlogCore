## Purpose

Define variables reutilizables e instancias validadas para capturar valores consistentes en instancias de redes sociales, manteniendo la lógica en modelos de Django.

## Requirements

### Requirement: Variables reutilizables administradas por staff
El sistema SHALL permitir que los usuarios staff creen, consulten, actualicen y eliminen variables reutilizables desde la administración. Cada variable SHALL tener un identificador único, un `label` de hasta 16 caracteres, una descripción de hasta 64 caracteres y una expresión regular que defina los valores aceptados. Los usuarios que no sean staff MUST NOT poder crear ni modificar variables.

#### Scenario: Staff registra una variable
- **WHEN** un usuario staff registra una variable con identificador, `label`, descripción y expresión regular válidos
- **THEN** la variable queda disponible para que otros contextos la configuren

#### Scenario: Usuario no staff intenta administrar variables
- **WHEN** un usuario no staff intenta crear o modificar una variable
- **THEN** el sistema rechaza la operación sin cambiar las variables disponibles

### Requirement: Instancias de variables validadas
El sistema SHALL permitir que una instancia de red social guarde múltiples instancias de variables. Cada instancia SHALL identificar la variable que define su valor y la instancia de red social a la que pertenece, y MUST validar el valor mediante una coincidencia completa con la expresión regular de esa variable antes de guardarlo. La propiedad y los permisos de la instancia de variable SHALL derivarse de su instancia de red social.

#### Scenario: Se guarda una instancia de variable válida
- **WHEN** un usuario proporciona un valor que coincide completamente con la expresión regular de una variable
- **THEN** el sistema guarda una instancia asociada a esa variable

#### Scenario: Se rechaza una instancia de variable inválida
- **WHEN** un usuario proporciona un valor que no coincide completamente con la expresión regular de una variable
- **THEN** el sistema rechaza el valor y no guarda la instancia

### Requirement: Instancias independientes, actualizables y archivables
El sistema SHALL mantener cada instancia de variable como un valor independiente de la definición de variable para que una misma variable pueda tener múltiples valores en distintas instancias de redes sociales. El autor de la instancia de red social padre SHALL poder actualizar el valor de una instancia de variable activa, sin cambiar su variable ni su instancia de red social. El autor SHALL poder archivar la instancia de variable, pero el sistema MUST NOT permitir su borrado físico ni cambios posteriores al archivado.

#### Scenario: Usuario actualiza una instancia de variable
- **WHEN** un usuario actualiza un valor válido en una instancia de variable que le pertenece
- **THEN** el sistema actualiza solo el valor de esa instancia y conserva su variable, instancia de red social y demás instancias sin cambios

#### Scenario: Usuario archiva una instancia de variable propia
- **WHEN** un usuario archiva una instancia de variable activa que le pertenece
- **THEN** el sistema conserva el registro como archivado y rechaza cambios o borrado físico posteriores

## OUT OF SCOPE

- Vistas, plantillas o URLs propias del proyecto para gestionar instancias de variables.
