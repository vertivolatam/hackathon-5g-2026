# field-monitoring/broca-trap-network

Red de monitoreo de broca del café (Coffee Berry Borer) derivada de `business/README.md` y de `business/00-fuentes-visuales/inferencia-imagenes.md`. Fuente de verdad del dominio; la instrumentación técnica vive en las otras dos capacidades.

## ADDED Requirements

### Requirement: Flujo trampa → alerta en 5 pasos

El sistema SHALL implementar el flujo: trampa captura y analiza en borde (Edge AI) → envía resumen por LoRa a gateway → gateway transmite por 5G → Edge/Nube procesa, almacena y genera alertas → RuralIA visualiza y gestiona.

#### Scenario: Evento de actividad alta

- WHEN una trampa registra aumento de actividad de broca
- THEN la plataforma SHALL mostrar la zona afectada y SHALL emitir una alerta temprana con recomendación de manejo.

### Requirement: Trampa autónoma con atrayente específico

Cada trampa SHALL operar con panel solar + batería, cámara con IA en borde, atrayente metanol + etanol, captura selectiva y GPS para ubicación en mapa.

#### Scenario: Reporte de trampa

- WHEN una trampa envía su resumen LoRa (estado, eventos, conteos IA)
- THEN el gateway SHALL asociarlo a su GPS y SHALL reenviarlo sin requerir la imagen cruda.

### Requirement: Gateway multi-modelo hacia la misma red 5G

La topología SHALL soportar como gateway cualquiera de: Dragino LoRaWAN (concentrador de nodos) + Nokia FRRx502e (interior) / Nokia FRRO501c (exterior) / Teltonika RUTX11, con alcances LoRaWAN 2–15 km y terminal Nokia XR20 contra la plataforma.

#### Scenario: Sustitución de gateway

- WHEN se cambia el modelo de gateway en una finca
- THEN los nodos LoRaWAN y la plataforma SHALL seguir operando sin cambios de protocolo.

### Requirement: Escalabilidad del MVP a red regional

El diseño SHALL pasar de 1 trampa (MVP) a red de trampas/fincas/regiones y a otras plagas y cultivos, integrando clima y mapas, sin cambiar el flujo de 5 pasos.

#### Scenario: Segunda finca

- WHEN se añade una finca con sus trampas y gateway
- THEN sus eventos SHALL agregarse al historial y tendencias existentes por zona.
