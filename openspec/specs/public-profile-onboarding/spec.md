## Purpose

Permitir que cada usuario staff complete su identidad pública en Django admin antes de acceder a las herramientas autorizadas por sus grupos.

## Requirements

### Requirement: Restricción de admin para perfiles pendientes
El sistema SHALL permitir el flujo de onboarding únicamente a cuentas activas con acceso staff a Django admin. Una cuenta staff sin perfil público SHALL ser dirigida al formulario de creación de su perfil desde cualquier herramienta de `/admin/`; las rutas de inicio de sesión, creación del perfil y cierre de sesión MUST permanecer disponibles. Una cuenta staff con perfil público SHALL acceder sólo a las herramientas para las que sus grupos o permisos le concedan acceso.

#### Scenario: Usuario staff sin perfil inicia sesión
- **WHEN** una cuenta staff sin perfil público inicia sesión en `/admin/`
- **THEN** el sistema la dirige al formulario de creación de su propio perfil público y no muestra herramientas administrativas

#### Scenario: Usuario con perfil accede a herramientas autorizadas
- **WHEN** una cuenta staff con perfil público accede a `/admin/`
- **THEN** el sistema muestra únicamente las herramientas para las que tiene permisos

#### Scenario: Usuario sin perfil abre una herramienta administrativa
- **WHEN** una cuenta staff sin perfil público solicita una ruta de herramienta de `/admin/` distinta del formulario de creación o del cierre de sesión
- **THEN** el sistema lo dirige al formulario de creación de su propio perfil público

### Requirement: Grupos de onboarding y herramientas
El sistema SHALL proporcionar un grupo de onboarding para cuentas staff sin perfil público que conceda únicamente el permiso necesario para crear `PublicProfile`. Los grupos de herramientas SHALL determinar las herramientas administrativas disponibles después del onboarding. El sistema MUST no cambiar automáticamente los grupos de una cuenta al crear su perfil; un administrador SHALL asignar manualmente los grupos de herramientas.

#### Scenario: Cuenta pendiente tiene sólo permiso de alta
- **WHEN** una cuenta staff pertenece al grupo de onboarding y no tiene perfil público
- **THEN** la cuenta puede abrir y enviar el formulario de creación de su propio perfil, pero no puede usar otras herramientas administrativas

#### Scenario: Administrador asigna herramientas manualmente
- **WHEN** un administrador asigna a una cuenta con perfil público un grupo que concede permisos de herramientas
- **THEN** la cuenta puede acceder a las herramientas concedidas por ese grupo

#### Scenario: Creación de perfil no cambia grupos
- **WHEN** una cuenta staff crea correctamente su perfil público
- **THEN** el sistema conserva sin cambios sus grupos existentes

### Requirement: Formulario de creación vinculado a la sesión
El sistema SHALL mostrar a las cuentas staff sin perfil público un formulario para proporcionar los datos obligatorios de su perfil mediante la interfaz y los componentes nativos de Django admin. El formulario SHALL inicializar `public_username`, `first_name` y `last_name` con los valores de la cuenta autenticada cuando estos estén disponibles, permitiendo al usuario modificar esos valores antes de guardar. El sistema MAY usar un único override de template de Django admin, limitado al formulario de `PublicProfile`, para ocultar la navegación de breadcrumbs y la barra lateral. El formulario MUST no permitir seleccionar ni proporcionar un usuario de autenticación; el perfil creado MUST asociarse al usuario autenticado de la sesión.

#### Scenario: Usuario crea su propio perfil
- **WHEN** una cuenta staff sin perfil envía datos de perfil válidos
- **THEN** el sistema crea un perfil público asociado a ese usuario autenticado

#### Scenario: Formulario no expone selección de usuario
- **WHEN** una cuenta staff visualiza el formulario de creación de perfil
- **THEN** el formulario no muestra un selector ni un campo editable para el usuario de autenticación

#### Scenario: Formulario prellena datos de la cuenta autenticada
- **WHEN** una cuenta staff abre el formulario de creación de perfil y tiene nombre de usuario, nombre o apellido
- **THEN** el sistema inicializa `public_username`, `first_name` y `last_name` con esos datos sin cambiar la asociación de usuario del perfil

#### Scenario: Formulario usa componentes nativos de Django admin
- **WHEN** una cuenta staff sin perfil abre el formulario de creación
- **THEN** el sistema muestra los estilos, componentes y errores de validación propios de Django admin

#### Scenario: Formulario oculta navegación administrativa no necesaria
- **WHEN** un usuario autenticado abre el formulario de creación o edición de su perfil público
- **THEN** el sistema no muestra breadcrumbs ni barra lateral y conserva el navbar con la opción de cerrar sesión

### Requirement: Acceso a herramientas tras completar el perfil
El sistema SHALL conceder acceso a herramientas administrativas sólo después de que la cuenta staff haya creado su perfil público con todos los datos obligatorios válidos y tenga los permisos correspondientes. Si los datos enviados no son válidos, el sistema MUST mostrar los errores y mantener al usuario en el flujo de creación sin conceder acceso a herramientas.

#### Scenario: Creación completada correctamente
- **WHEN** el usuario envía todos los datos obligatorios válidos del perfil
- **THEN** el sistema guarda el perfil y muestra las herramientas autorizadas por los grupos existentes de la cuenta

#### Scenario: Datos de perfil inválidos
- **WHEN** el usuario envía datos obligatorios ausentes o inválidos
- **THEN** el sistema no crea el perfil, muestra los errores de validación y no permite acceder a herramientas administrativas
