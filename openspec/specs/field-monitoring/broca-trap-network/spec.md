# field-monitoring/broca-trap-network Specification

## Purpose

Red de monitoreo de broca del café (Coffee Berry Borer) derivada de `business/README.md` y de `business/00-fuentes-visuales/inferencia-imagenes.md`. Fuente de verdad del dominio; la instrumentación técnica vive en las otras dos capacidades.

## Requirements

### Requirement: Flujo trampa → alerta en 5 pasos

El sistema SHALL implementar el flujo: trampa captura y analiza en borde (Edge AI) → envía resumen por LoRa a gateway → gateway transmite por 5G → Edge/Nube procesa, almacena y genera alertas → AgriVision visualiza y gestiona.

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

### Requirement: Red privada 5G standalone (NPN)

Trampas y gateway SHALL registrarse al PLMN privado (SA, SIMs propias, `AT+COPS` manual), sin depender de cobertura comercial: una DNN por finca (`agrivision.<customer-id>`, sin device-id en el DNN; la identidad del equipo vive en SIM/MQTT/TLS), telemetría y fotos separadas por 5QI si el core lo soporta o por prioridad en app si es best-effort único, con breakout local al core en finca. La finca SHALL operar sin internet ni operadoras.

#### Scenario: Finca sin cobertura comercial

- WHEN la finca no tiene señal de ningún operador
- THEN trampas y gateway SHALL seguir publicando contra el core privado y las alertas SHALL generarse on-prem.

### Requirement: Confiabilidad demostrable del enlace 5G

Cada trampa SHALL reportar registro y RSSI (`rssi_dbm` en telemetría), el backend SHALL exponerlo en `/metrics` por trampa y Grafana SHALL graficarlo. La instalación SHALL validarse con el procedimiento de `docs-site/docs/how-to/validar-enlace-5g.md` (attach ≥95%, RSSI ≥ -95 dBm, soak 24 h sin huecos, foto punta a punta).

#### Scenario: Trampa con mala señal

- WHEN el RSSI medido es < -95 dBm
- THEN la instalación SHALL reubicar trampa/antena antes de darla por operativa.

## Referencias

- <https://youtu.be/hLMtsCWPOg8>
- <https://gitlab.com/Athamaxy/telegram-bot-tutorial/-/blob/main/TutorialBot.py>
- <https://grafana.com/blog/how-to-embed-grafana-dashboards-into-web-applications/>
- <https://serverless.roboflow.com>
- <https://console.west.us.dac.nokia.com/user/login>
- <https://ndt.enso.saas.nokia.com>
- <https://nidm.enso.saas.nokia.com/pages/home>
- <https://thingsdata.es/knowledge-base-es/mmtc-explicacion/>
- <https://app.scalefusion.com/cloud/dashboard/devices>
- <https://github.com/kubernetes/minikube/issues/8426>
- <https://github.com/kubernetes/minikube/issues/9024>
