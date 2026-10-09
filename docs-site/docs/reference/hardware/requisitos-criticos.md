---
sidebar_position: 1
---

# Requisitos críticos del hardware

Fuente única de los mínimos no negociables por subsistema. Detalle en cada ficha de `reference/hardware/`.

## Trampa (×1.000, una por cafeto)

| Subsistema | Requisito crítico | Fuente |
|---|---|---|
| Cómputo | ESP32-P4-NANO: 32 MB PSRAM, MIPI-CSI 2-lane con ISP, Ethernet/Wi-Fi 6, PoE opcional | [ficha](esp32-p4-nano) |
| Módem 5G | Quectel RG255C-GL RedCap R17, sleep ~2.8 mA / idle ~25 mA, USB 2.0 + UART-AT, SA + LTE Cat 4 fallback | [ficha](rg255c-redcap) |
| Antenas celular | **YECN028AA ×2 por trampa**: 5.5 dBi, 600–960 / 1710–2690 / 3300–6000 MHz, omni, SMA macho, **IP66**, −40/+85 °C, 225×54.5×13 mm. Elegida sobre YECN009AA (5.8 dBi pero sin IP declarado) y YECT104WAAM (IP67 pero 3.9 dBi + conector N) | Quectel antenna brochure pp. 6–14 |
| Antena GNSS | ×1 por trampa (multiconstelación del RG255C) | [ficha](rg255c-redcap) |
| Cámara | AR1335 13 MP (final, vía adaptador FPC: EVK de 70 pines, CSI a 2 lanes) u OV5647 5 MP (PoC del KIT-C) | [ficha](tevm-ar1335) |
| Bomba atrayente | Atlas EZO-PMP por I2C 0x67, ±1%, mínimo 0.5 ml; **motor 12–24V** (riel dedicado en placa) | [ficha](ezo-pmp) |
| Luz | BH1750 en 0x23, umbral noche 10 lx + iluminador ~3W (LED blanco/IR por MOSFET) | [ficha](bh1750) |
| Energía | Solar + LiFePO4; rieles 3.3V / 5V / **12V**; presupuesto ~3.3 Wh/día (+ iluminador de noche) | Decisión 5 |

## Sensores de la trampa

| Sensor | Estado | Notas |
|---|---|---|
| Temperatura + humedad | Placeholder DHT22/DS18B20 en `read_sensors()`; **modelo final por definir** (candidato: SHT35 por precisión ±1.5%RH en campo húmedo) | Telemetría `temp_c`, `hum_pct` |
| Conteo de capturas | **Por definir**: haz IR break-beam en la entrada (bajo consumo, sin cámara) o conteo por visión | Telemetría `count` (hoy 0 fijo) |
| Posición GPS | Sin hardware extra: **GNSS del RG255C** (1 Hz máx, antena dedicada) | Spec red de monitoreo exige ubicación en mapa |
| Luz (día/noche) | ✅ BH1750 0x23 + iluminador | [ficha](bh1750) |
| IMU | Presente en la AR1335 (LSM6DSO16IS), **sin uso** asignado | Reservada: detección de vandalismo/movimiento futuro |

## Gateway (por finca)

| Subsistema | Requisito crítico | Fuente |
|---|---|---|
| Cómputo | Raspberry Pi 4 64-bit, balenaOS, `agent.py` como servicio | balena/ |
| Módem 5G | Quectel **RM520N-GL** (eMBB backhaul; descartado RM530N: mmWave inútil + sin certs US) por USB 3.0 MBIM + **5V/3A externos** | [ficha](rm520n-gl-vs-rm530n-gl) |
| Antenas celular | **YECN028AA ×4** (mismo modelo que trampas: un solo repuesto) | Quectel antenna brochure pp. 6–14 |
| Antena GNSS | En ANT3 del módulo (posicionamiento 1 Hz máx) | [ficha](rm520n-gl-vs-rm530n-gl) |

## Red (NPN privada, sin operadoras ni slicing)

| Requisito crítico | Fuente |
|---|---|
| 5G SA sub-6, DNN por finca `agrivision.<customer-id>`, PLMN + SIMs propias | Decisión 5 |
| Tópicos `agrivision/<cli>/<finca>/<trampa>/*`; binarios por HTTP, eventos por MQTT | [tópicos](../mqtt-topics) |
| mMTC como escenario (densidad) + fotos perfil-eMBB | [mMTC](mmtc-escenario) |
| Vendor RAN/core con RedCap R17 real + espectro autorizado ante SUTEL | Decisión 5 |
