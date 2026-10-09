---
sidebar_position: 1
---

# Requisitos críticos del hardware

Fuente única de los mínimos no negociables por subsistema. Detalle en cada ficha de `reference/hardware/`.

> Precios de referencia (oct-2026, unitario salvo nota) para el modelo de costos. **Verificar al comprar**: varían por volumen y distribuidor; los módulos Quectel suelen bajar 10–20% a 250+ y 1.000+ uds.

## Trampa (×1.000, una por cafeto)

| Subsistema | Requisito crítico | Compra | Precio ref | Fuente |
|---|---|---|---|---|
| Cómputo | ESP32-P4-NANO **KIT-C** (placa + PoE + RPi Camera OV5647 5 MP): 32 MB PSRAM, MIPI-CSI 2-lane con ISP, Wi-Fi 6, PoE | [waveshare.com/esp32-p4-nano](https://www.waveshare.com/esp32-p4-nano.htm) | $19–87 según kit (KIT-C en rango alto, verificar) | [ficha](esp32-p4-nano) |
| Módem 5G | **TOP #1: Quectel RG255C-GL M.2** RedCap R17 (X35), sleep ~2.8 mA / idle ~25 mA, USB 2.0 + UART-AT, SA + LTE Cat 4 fallback. Alternativa: RM255C-GL. Descartados: RG255AA, RG255G | [5gwave.com](https://5gwave.com/products/quectel-rg255c-gl-5g-redcap-m-2) · [TOP-electronics](https://www.top-electronics.com/en/5g-redcap-rg255c-gl-m-2) | ~$130–210 (€129.92 / $150 / $209 según distribuidor) | [ficha](rg255c-redcap) |
| Antenas celular | **YECN028AA ×2 por trampa**: 5.8 dBi, 410–470 / 617–960 / 1427–6000 MHz, omni, SMA macho, **IP66**, −40/+85 °C, 225×54.5×13 mm. Elegida sobre YECN009AA (3.4 dBi, sin IP) y YECT104WAAM (IP67 pero 3.9 dBi + conector N) | [524wifi.net](https://524wifi.net/product/quectel-yecn028aa-ultra-wide-band-5g-ntn-cellular-terminal-dipole-antenna-410-6000mhz-lte-sma-male-black-6dbi-ip66/) · [TOP-electronics](https://www.top-electronics.com/en/5g-ntn-terminal-mount-ext-antenna) | ~$7–20 ($6.90 / €10.19 / $19.99) | Quectel antenna brochure pp. 6–14 |
| Antena GNSS | ×1 por trampa (multiconstelación del RG255C; mismo formato SMA) | Mismo distribuidor que celular | ~$5–15 (cotizar con el lote) | [ficha](rg255c-redcap) |
| Cámara | AR1335 13 MP (final, vía adaptador FPC: EVK de 70 pines, CSI a 2 lanes) u OV5647 5 MP (PoC incluida en el KIT-C) | [technexion.com](https://www.technexion.com/shop/embedded-vision/mipi-csi2/evk/70-pin/tevm-ar1335-c-s85-ir-evk/) | **$147** (1–50; $135.85 a 51+, $127.10 a 200+) | [ficha](tevm-ar1335) |
| Bomba atrayente | Atlas EZO-PMP por I2C 0x67, ±1%, mínimo 0.5 ml; **motor 12–24V** (riel dedicado en placa) | [atlas-scientific.com](https://atlas-scientific.com/peristaltic/ezo-pmp/) | **$94.99** ($89.99 a 4+, $85.99 a 25+) | [ficha](ezo-pmp) |
| Luz | BH1750 en 0x23, umbral noche 10 lx + iluminador ~3W (LED blanco/IR por MOSFET) | [adafruit.com](https://www.adafruit.com/product/4681) (ref; buscar GY-30 local ~$2.50) | ~$2.50–4.50 | [ficha](bh1750) |
| Energía | Solar + LiFePO4; rieles 3.3V / 5V / **12V**; presupuesto ~3.3 Wh/día (+ iluminador de noche). Panel + batería + MPPT: **cotizar por volumen** | — | TBD (dimensionar con ~3.3 Wh/día) | Decisión 5 |

## Sensores de la trampa

| Sensor | Estado | Notas |
|---|---|---|
| Temperatura + humedad | Placeholder DHT22/DS18B20 en `read_sensors()`; **modelo final por definir** (candidato: SHT35 por precisión ±1.5%RH en campo húmedo) | Telemetría `temp_c`, `hum_pct` |
| Conteo de capturas | **Por definir**: haz IR break-beam en la entrada (bajo consumo, sin cámara) o conteo por visión | Telemetría `count` (hoy 0 fijo) |
| Posición GPS | Sin hardware extra: **GNSS del RG255C** (1 Hz máx, antena dedicada) | Spec red de monitoreo exige ubicación en mapa |
| Luz (día/noche) | ✅ BH1750 0x23 + iluminador | [ficha](bh1750) |
| IMU | Presente en la AR1335 (LSM6DSO16IS), **sin uso** asignado | Reservada: detección de vandalismo/movimiento futuro |

## Gateway (por finca — 1 por finca, NO por trampa)

> Las trampas ya llevan ESP32-P4 + 5G propio: el gateway **no es por cafeto**. Existe uno por finca para comisionado, respaldo y PoC; cuando el 100% de trampas tenga 5G directo a la NPN, se elimina sin cambiar protocolo (ver Decisión 5). Un ESP32 **no** lo sustituye: sin Linux no hay drivers MBIM del HAT, ni agent.py, ni gestión de flota Balena.

| Subsistema | Requisito crítico | Compra | Precio ref | Fuente |
|---|---|---|---|---|
| Cómputo | Raspberry Pi 4 64-bit, balenaOS, `agent.py` como servicio | Distribuidor local / PiShop | ~$35–75 según RAM (volátil, verificar) | balena/ |
| Módem 5G | Quectel **RM520N-GL** (eMBB backhaul; descartado RM530N) por USB 3.0 MBIM + **5V/3A externos**. HAT portadora M.2→USB aparte | [waveshare.com/rm520n-gl](https://www.waveshare.com/rm520n-gl.htm) (módulo) | **$272.99** módulo (HAT aparte, cotizar) | [ficha](rm520n-gl-vs-rm530n-gl) |
| Antenas celular | **YECN028AA ×4** (mismo modelo que trampas: un solo repuesto) | Ver trampa | ~$7–20 c/u | Quectel antenna brochure pp. 6–14 |
| Antena GNSS | En ANT3 del módulo (posicionamiento 1 Hz máx) | Ver trampa | ~$5–15 | [ficha](rm520n-gl-vs-rm530n-gl) |

## Red (NPN privada, sin operadoras ni slicing)

| Requisito crítico | Fuente |
|---|---|
| 5G SA sub-6, DNN por finca `agrivision.<customer-id>`, PLMN + SIMs propias | Decisión 5 |
| Tópicos `agrivision/<cli>/<finca>/<trampa>/*`; binarios por HTTP, eventos por MQTT | [tópicos](../mqtt-topics) |
| mMTC como escenario (densidad) + fotos perfil-eMBB | [mMTC](mmtc-escenario) |
| Vendor RAN/core con RedCap R17 real + espectro autorizado ante SUTEL | Decisión 5 |
