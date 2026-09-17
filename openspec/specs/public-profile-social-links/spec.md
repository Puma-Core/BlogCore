# public-profile-social-links Specification

## Purpose

Permitir que cada perfil público seleccione y consulte los enlaces de redes sociales activos que desea presentar, usando las instancias y valores ya configurados por su propietario.

## Requirements

### Requirement: Perfil público selecciona sus instancias de redes sociales
El sistema SHALL permitir que un perfil público relacione cero o más instancias de redes sociales de su usuario propietario. Cada relación SHALL identificar una única instancia de red social y MUST impedir que la misma instancia se relacione más de una vez con el mismo perfil.

#### Scenario: Perfil agrega una red social propia
- **WHEN** se relaciona una instancia de red social activa cuyo autor es el usuario del perfil público
- **THEN** la instancia queda seleccionada por el perfil público

#### Scenario: Perfil intenta agregar la misma red dos veces
- **WHEN** se intenta relacionar por segunda vez la misma instancia de red social con un perfil público
- **THEN** el sistema rechaza la relación duplicada y conserva una única selección

### Requirement: Perfil público solo expone enlaces sociales utilizables
El sistema SHALL exponer las instancias de redes sociales seleccionadas por un perfil público que estén activas y pertenezcan a su usuario propietario. Cada enlace SHALL conservar la URL e ícono resueltos por su configuración y sus instancias de variables. El sistema MUST NOT incluir instancias archivadas ni instancias cuyo autor no sea el propietario del perfil.

#### Scenario: Perfil consulta una red social seleccionada y completa
- **WHEN** el perfil público tiene seleccionada una instancia activa propia con todos los valores requeridos para resolver su URL
- **THEN** la red social queda disponible desde el perfil con su URL e ícono resueltos

#### Scenario: Red social seleccionada se archiva
- **WHEN** una instancia seleccionada por un perfil público se archiva
- **THEN** el perfil deja de incluirla entre sus enlaces sociales disponibles

#### Scenario: Perfil intenta relacionar una red de otro usuario
- **WHEN** se intenta relacionar con un perfil público una instancia de red social creada por otro usuario
- **THEN** el sistema rechaza la relación y no la expone desde el perfil
