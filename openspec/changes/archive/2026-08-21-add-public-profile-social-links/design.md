## Context

El proyecto usa el modelo `auth.User` de Django y solo tiene la aplicación `posts`. No se expondrán vistas, plantillas ni URLs propias para dashboard o perfiles públicos; la funcionalidad se limita a modelos, formularios, validaciones y Django admin. Véanse `proposal.md` y los delta specs para la motivación y los requisitos de comportamiento.

## Goals / Non-Goals

**Goals:**
- Añadir una aplicación de perfiles que concentre las definiciones de variables, configuraciones de redes sociales, la información pública y las instancias de cada usuario.
- Mantener la administración de definiciones separada de la edición que realiza un usuario sobre sus propias instancias.
- Validar los valores de variables tanto en el formulario como en el modelo para que no puedan persistirse valores inválidos por rutas alternativas.
- Definir modelos, formularios y reglas de validación para perfiles públicos e instancias de redes sociales, sin implementar vistas, plantillas ni URLs propias del proyecto.
- Aplicar TDD a cada capacidad mediante ciclos red-green-refactor antes de incorporar su funcionalidad.

**Non-Goals:**
- No sustituir el modelo `auth.User` existente ni implementar registro, autenticación o recuperación de cuenta.
- No importar automáticamente datos desde proveedores externos ni verificar la propiedad de una cuenta social.
- No implementar vistas, plantillas ni URLs propias del proyecto para dashboard o presentación pública del perfil.
- No incluir un sistema de seguimiento, analíticas, orden personalizado de enlaces o una API pública en esta primera entrega.

## Decisions

### Aplicación y modelo de datos dedicados

Se creará una aplicación `profiles` con cinco modelos. `Variable` y `VariableInstance` forman una capacidad independiente: la primera define un identificador reutilizable, `label`, descripción y expresión regular; la segunda persiste un valor validado asociado a una instancia de red social. `SocialNetworkConfig` es la única definición de red social: contiene nombre, `template_url`, `icon_url` y las variables que utiliza. `PublicProfile`, relacionado uno a uno con `auth.User`, contiene los datos públicos, un `public_username` único y una `photo_url` opcional. `SocialNetworkInstance` representa una configuración elegida por un usuario, conserva su autor inmutable y es la única fuente de propiedad para sus instancias de variables.

Las relaciones serán `SocialNetworkConfig N:M Variable`, `auth.User 1:N SocialNetworkInstance N:1 SocialNetworkConfig` y `SocialNetworkInstance 1:N VariableInstance N:1 Variable`. Esta separación permite reutilizar variables entre configuraciones, que una configuración solicite varios valores y que un usuario tenga varias instancias. La spec `social-variables` define el contrato de variables e instancias; la spec de configuraciones de redes sociales define qué variables consume cada configuración. Se descarta añadir campos al usuario actual porque Django ya usa `auth.User` y cambiarlo requeriría una migración de autenticación innecesaria.

### Plantillas de URL y validación centralizada

Cada `SocialNetworkConfig` almacenará `template_url` e `icon_url`, y asociará las variables que puede consumir. La configuración validará que toda referencia de `template_url` pertenece a una de sus variables asociadas. Un validador propio será llamado por `VariableInstance.clean()` para comprobar una coincidencia completa contra el `regex` de la variable, además de comprobar que la variable está asociada a la configuración de su `SocialNetworkInstance`. La URL del enlace y el ícono se derivarán de la configuración y de los valores validados.

Se descarta guardar una URL arbitraria porque impediría garantizar la relación entre la plataforma, sus variables y sus valores validados. También se descarta codificar las redes o variables en una lista estática, ya que el personal staff debe poder administrarlas sin desplegar código.

### Límites de acceso por superficie

`Variable` y `SocialNetworkConfig` serán registrados en Django admin y sus operaciones de escritura estarán restringidas por los permisos estándar de Django, disponibles solo a staff. Las instancias de redes sociales y los valores de variables heredan la propiedad del autor de la instancia padre; el modelo impide cambiar el autor y bloquea modificaciones una vez archivada la instancia. El perfil público y sus instancias se gestionarán como modelos de Django sin exponer vistas propias.

Esta estrategia reutiliza los límites de seguridad ya provistos por el admin y mantiene las reglas de propiedad e inmutabilidad en el modelo, sin depender de vistas ni parámetros de URL editables.

### Propiedad inmutable y archivado

Las instancias de red social registrarán su autor al crearse. Ese vínculo no admitirá actualización por ningún actor. Las instancias de variable no almacenarán autor: su propiedad y permisos derivarán exclusivamente de la instancia de red social padre. El propietario de la instancia de red podrá actualizar únicamente los datos funcionales de las instancias activas y archivarlas en vez de borrarlas. El archivado preservará el registro para auditoría, bloqueará cambios posteriores y excluirá la instancia de los enlaces construidos por el modelo.

Se descarta el borrado físico porque elimina la trazabilidad de quién creó una instancia de red y de sus valores publicados. Se descarta un autor duplicado en instancias de variables porque su propiedad queda determinada de forma inequívoca por la instancia de red padre.

### Perfil público y foto externa

El perfil público se mantendrá como un modelo de Django relacionado uno a uno con `auth.User`, identificado por `public_username` y con los campos públicos deseados. La foto se representará mediante una `photo_url` opcional validada como URL externa. No se implementarán vistas, plantillas ni URLs propias para la edición ni la presentación del perfil.

Se descarta la subida de archivos porque requeriría definir almacenamiento, entrega de media y gestión de recursos. La validación comprobará la estructura de la URL, no la disponibilidad ni el contenido remoto de la imagen.

### Desarrollo guiado por pruebas

Cada capacidad se implementará con el ciclo red-green-refactor: primero una prueba que exprese el escenario del spec y falle, después la implementación mínima que la haga pasar y finalmente la simplificación sin cambiar comportamiento. Las tareas se agrupan por capacidad para evitar implementar primero todos los modelos y probarlos al final.

El plan de la rama padre conserva únicamente sus tareas aprobadas. Si una rama hija de implementación descubre una tarea nueva, la registrará como `+=<número>` en su seguimiento de ejecución, sin renumerar ni modificar el plan aprobado.

## Risks / Trade-offs

- [Una plantilla puede referenciar variables no asociadas y generar enlaces incompletos] → Validar las referencias de `template_url` contra `SocialNetworkConfig` al guardar la configuración y cubrirlo con pruebas de modelo y admin.
- [Cambiar el `regex` de una variable puede volver inválidos valores ya guardados] → Las reglas nuevas se aplican a escrituras futuras; el admin debe advertir que las modificaciones no reescriben los valores existentes.
- [Una instancia puede ser reasignada o eliminada y perder trazabilidad] → Hacer inmutable el autor y aplicar archivado sin borrado físico, con pruebas de propiedad y exclusión pública.
- [Una imagen externa puede no estar disponible o cambiar fuera del sistema] → Validar la estructura de `photo_url`; quien consuma el modelo decidirá cómo manejar la ausencia de imagen.
- [Un usuario sin perfil podría intentar acceder a datos inexistentes] → El modelo expone el perfil mediante `public_username`; cualquier consumidor futuro debe manejar la ausencia sin exponer información privada.

## Migration Plan

1. Añadir la aplicación y los modelos con sus restricciones y relaciones.
2. Generar y aplicar las migraciones del nuevo esquema.
3. Registrar las definiciones de red y variables en Django admin.
4. Verificar permisos, configuración, valores y campos del perfil público mediante pruebas de Django y `manage.py check`.
5. Si se requiere reversión, retirar el registro del admin y revertir la migración de la aplicación; al no haber vistas ni archivos media propios, no hay elementos adicionales que limpiar.
