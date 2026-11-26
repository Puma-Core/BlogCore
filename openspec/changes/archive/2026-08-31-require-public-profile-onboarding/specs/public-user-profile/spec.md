## ADDED Requirements

### Requirement: Propiedad inmutable del perfil público
El sistema SHALL asociar cada perfil público con la cuenta staff que lo crea desde su sesión autenticada, incluso cuando dicha cuenta tenga privilegios de superusuario. Una vez creado el perfil, esa asociación MUST permanecer inmutable y ningún flujo de edición del perfil puede reasignarlo a otra cuenta de autenticación.

#### Scenario: Perfil asociado al usuario autenticado
- **WHEN** un usuario autenticado crea su perfil público mediante el flujo de onboarding
- **THEN** el perfil queda asociado únicamente a ese usuario de autenticación

#### Scenario: No se puede reasignar el propietario
- **WHEN** se intenta modificar un perfil público existente mediante un flujo de edición
- **THEN** el sistema conserva el usuario de autenticación asociado originalmente

#### Scenario: Staff crea únicamente su propio perfil
- **WHEN** una cuenta staff sin perfil crea un perfil público mediante el flujo de onboarding
- **THEN** el perfil queda asociado a esa cuenta staff y no a otra cuenta de autenticación
