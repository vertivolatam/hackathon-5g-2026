---
sidebar_position: 3
---

# TEVM-AR1335 (cámara de la trampa)

Ficha del sensor. Fuente: [technexion.com — TEVM-AR1335-C-S85-IR-EVK](https://www.technexion.com/shop/embedded-vision/mipi-csi2/evk/70-pin/tevm-ar1335-c-s85-ir-evk/)

## Sensor onsemi AR1335

- 13 MP (4208×3120), píxel BSI 1.1 µm, formato 1/3.2", **rolling shutter**, color.
- MIPI CSI-2 **hasta 4 lanes** + I2C; salidas YUV/RGB/JPEG/**MJPEG**/RAW8-12.
- Ritmos útiles: 1080p@60 · 720p@120 · 4K@10-15 (el backend acepta JPEG en base64, ver `POST /api/detect`).
- Consumo ≤ 723 mW; −30…+70 °C; 24.5×24.5 mm, ≤ 12 g.
- Lente M12 85° (D-FOV 84.6°) con **filtro IR-cut 650 nm** (color diurno real) + IMU a bordo (innecesaria para trampa fija).

## Desajustes de integración (leer antes de comprar cables)

1. **Conector de 70 pines para SOMs NXP i.MX** (i.MX8M/93/95). No enchufa directo ni al ESP32-P4-NANO ni al Pi: hace falta el cable/adaptador FPC al pinout CSI del destino, o validar el ponga del kit.
2. **ESP32-P4-NANO = CSI de 2 lanes**. El sensor baja a 2 lanes sin problema; dimensionar el pipeline a 1080p (suficiente para broca, 1–3 mm a corta distancia con lente 85°).
3. Mientras llega el adaptador, el **KIT-C del ESP32-P4-NANO trae OV5647 5MP** que valida el pipeline completo sin la AR1335.

## Implicaciones de firmware

- El probe SCCB de `apps/esp-32/drivers/camera.py` ya cubre `0x36/0x30/0x3C`; con la AR1335 montada debe dar ACK (si no, revisar el adaptador FPC, no el firmware).
- Captura real: ESP-IDF `esp_video` (CSI + ISP + JPEG) en el P4, o captura USB en el gateway como PoC.
