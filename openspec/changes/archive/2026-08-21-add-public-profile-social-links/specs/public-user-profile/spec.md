## Purpose

Ofrecer una identidad pública configurable para cada usuario a través de un modelo de Django, manteniendo los datos y las reglas de validación disponibles para futuros consumidores.

## ADDED Requirements

### Requirement: Perfil público identificado por nombre de usuario público
El sistema SHALL mantener un perfil público por usuario que incluya un `public_username` único, nombre, apellido, título, subtítulo, especialidad, descripción corta, `photo_url` opcional y redes sociales instanciadas. Cuando se proporcione, `photo_url` MUST ser una URL válida de una imagen externa. El `public_username` SHALL identificar al perfil y la información guardada SHALL estar disponible para consulta desde el modelo.

#### Scenario: Se persiste un perfil configurado
- **WHEN** se crea o actualiza un perfil con `public_username` válido y campos públicos
- **THEN** el sistema guarda los datos y los expone a través del modelo

#### Scenario: Se intenta elegir un nombre público existente
- **WHEN** se intenta guardar un `public_username` ya asignado a otro perfil
- **THEN** el sistema rechaza el cambio y conserva el nombre público existente

#### Scenario: Se guarda una URL de foto válida
- **WHEN** se proporciona una `photo_url` válida al actualizar el perfil
- **THEN** el sistema guarda la URL para que los futuros consumidores la utilicen

### Requirement: Validación del perfil público
El sistema SHALL validar los campos del perfil público antes de guardarlos. El `photo_url` MUST ser una URL externa válida o estar en blanco. El `public_username` MUST ser único y obligatorio.

#### Scenario: Se rechaza una URL de foto inválida
- **WHEN** se proporciona una `photo_url` que no es una URL válida
- **THEN** el sistema rechaza el valor y no guarda el perfil

## OUT OF SCOPE

- Vistas, plantillas o URLs propias del proyecto para editar o presentar el perfil.
- Dashboard de gestión de instancias de redes sociales.
