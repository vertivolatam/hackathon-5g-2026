---
sidebar_position: 5
---

# mMTC como escenario (marco del jurado)

Fuente: [ThingsData — mMTC explicación](https://thingsdata.es/knowledge-base-es/mmtc-explicacion/) (16-sep-2021).

## Qué dice la fuente

- mMTC (massive Machine Type Communication) es **uno de los tres escenarios 5G** junto a eMBB (velocidad) y URLLC (latencia). Su eje es la **escala**: miles/millones de dispositivos con mensajes pequeños y esporádicos.
- Rasgos: altísima densidad de conexiones por celda, bajo consumo (años de batería), bajo costo por dispositivo, paquetes pequeños.
- Portadoras clásicas: **NB-IoT y LTE-M** (tecnologías 4G incorporadas al marco 5G).
- Aplicaciones: contadores, smart city, asset tracking, **sensores agrícolas**, monitorización de infraestructuras.
- Límites: baja velocidad, mayor latencia, y **disponibilidad de red según región**.
- Al implementar: elegir conectividad (NB-IoT vs LTE-M), diseñar el dispositivo para bajo consumo, definir frecuencia/volumen de datos e integrar a plataforma IoT.

## Lectura para AgriVision (honesta)

| Punto de la fuente | Nuestra posición |
|---|---|
| Densidad (1.000 trampas) | Es el requisito mMTC del jurado; se cubre con NPN privada + wake desfasado |
| Bajo consumo / años de batería | Duty-cycle con load-switches (`drivers/power.py`, ~3.3 Wh/día) |
| Mensajes pequeños y esporádicos | Telemetría MQTT siempre; **foto solo por evento** |
| NB-IoT / LTE-M | **No disponibles**: 0 menciones en los PDF Quectel y sin red comercial en CR; con NPN privada no aplican |
| Alta velocidad (fotos 13 MP) | **Fuera del perfil mMTC**: las fotos van por bearer eMBB (DNN de la finca), no por el perfil de telemetría |
| Disponibilidad según región | Resuelto con red privada: la finca no depende de ningún operador |

RedCap (RG255C, ver [ficha](./rg255c-redcap)) es el punto medio 5G-nativo: más capacidad que NB-IoT/LTE-M (suficiente para MQTT + JPEG por evento) con consumo y señalización muy por debajo del eMBB. Por eso el diseño es **telemetría perfil-mMTC + fotos perfil-eMBB**, ambas sobre la misma NPN.
