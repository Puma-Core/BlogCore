## Why

Las URLs firmadas emitidas por el servicio de buckets expiran tras una hora, por lo que las imágenes insertadas en documentos dejan de estar disponibles. Los adjuntos públicos deben conservar una URL estable servida desde el dominio personalizado de medios.

## What Changes

- Configurar el almacenamiento S3-compatible para generar URLs públicas sin parámetros de firma para los adjuntos.
- Usar el dominio personalizado configurado para construir las URLs de objetos remotos.
- Documentar las variables de entorno necesarias para la entrega pública desde el dominio personalizado.
- Cubrir con pruebas la configuración y las URLs devueltas al cargar o consultar adjuntos.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `post-media-storage`: las URLs de adjuntos en almacenamiento remoto deben poder ser públicas, permanentes y servidas desde un dominio personalizado configurado.

## Impact

- Código afectado: `project/app/settings.py`, configuración de contenedor y documentación de entorno.
- Comportamiento afectado: las respuestas de carga y consulta de adjuntos contienen URLs estables del dominio personalizado, en lugar de URLs firmadas que expiran.
- Infraestructura afectada: el bucket y el dominio personalizado deben permitir lectura pública de los objetos de adjuntos.
