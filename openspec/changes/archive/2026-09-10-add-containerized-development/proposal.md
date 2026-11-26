## Why

El proyecto no cuenta con un entorno de ejecución reproducible que permita desarrollar y servir Django sin depender del gestor de paquetes instalado en el host. Se necesita un contenedor de desarrollo que conserve la sincronización bidireccional del código y exponga el dashboard y las APIs a clientes externos.

## What Changes

- Añadir una imagen Docker basada en Alpine con Git, Python y uv para ejecutar el proyecto.
- Añadir una configuración Docker Compose que monte el repositorio actual en el contenedor y mantenga el entorno virtual exclusivamente dentro de este.
- Ejecutar la aplicación Django mediante su interfaz WSGI, escuchando en todas las interfaces y publicar su puerto para acceder al panel de administración y las APIs desde el host u otros clientes de red autorizados.
- Inyectar la configuración de ejecución, incluidos los hosts externos permitidos, mediante variables de entorno, sin eliminar los valores locales por defecto.
- Documentar el arranque del entorno y los comandos de desarrollo ejecutables mediante Docker Compose.

## Capabilities

### New Capabilities
- `containerized-development`: Entorno Docker Compose reproducible para desarrollar y servir la aplicación Django con código compartido y acceso de red externo.

### Modified Capabilities

- `project-foundation`: La configuración base debe admitir hosts permitidos configurables para servir la aplicación desde el contenedor.

## Impact

- Afecta a la configuración de Django en `project/app/settings.py`.
- Añade archivos de Docker, Docker Compose, exclusiones de contexto y documentación de uso.
- No añade servicios de infraestructura ni modifica los contratos existentes de las APIs.
