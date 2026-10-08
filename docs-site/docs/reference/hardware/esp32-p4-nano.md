---
sidebar_position: 1
---

# ESP32-P4-NANO (nodo de trampa)

Ficha del hardware real del leaf. Fuente: [waveshare.com/esp32-p4-nano](https://www.waveshare.com/esp32-p4-nano.htm) · Wiki: [docs.waveshare.com/ESP32-P4-NANO](https://docs.waveshare.com/ESP32-P4-NANO)

## SoC y memoria

- ESP32-P4: RISC-V dual-core de alto rendimiento + single-core de bajo consumo.
- 128 KB HP ROM · 16 KB LP ROM · 768 KB HP L2MEM · 32 KB LP SRAM · 8 KB TCM.
- **32 MB PSRAM en paquete** + 16 MB NOR Flash en placa.
- Seguridad: Secure Boot, Flash Encryption, aceleradores criptográficos, TRNG, firma digital y Key Management Unit.

## Visión y multimedia (clave para la trampa)

- **MIPI-CSI 2-lane con ISP integrado**, codec JPEG, encoder H264 y Pixel Processing Accelerator: captura, compresión y pre-proceso en borde sin CPU externa.
- MIPI-DSI 2-lane para display local.
- Límite físico: son **2 lanes**, no 4 — el sensor (ver [TEVM-AR1335](./tevm-ar1335)) negocia a 2 lanes.

## Conectividad y energía

- Ethernet 100M (RJ45 en placa) · USB OTG 2.0 HS · TF (SDIO 3.0) · micrófono y header de parlante.
- Wi-Fi 6 + BLE 5 vía módulo ESP32-C6 (protocolo SDIO).
- **Header para módulo PoE opcional**: datos + energía por un solo cable Ethernet — la opción lógica en finca.
- 28 GPIOs programables; periféricos: SPI, I2S, I2C, LED PWM, MCPWM, RMT, ADC, UART, TWAI.

## Kits

| Kit | Incluye | Uso en AgriVision |
|---|---|---|
| Básico | placa + parlante | bring-up sin cámara |
| **KIT-C (recomendado PoC)** | + PoE + **RPi Camera (B) OV5647 5MP** + FFC | PoC de visión inmediato, sin esperar adaptador AR1335 |
| KIT-D | + display DSI 10.1" | consola local de campo |

La RPi Camera (B) es OV5647 5MP, foco manual, F2.0, 60.6° — suficiente para validar el pipeline `/api/detect` antes de la AR1335.

## Implicaciones de firmware

- MicroPython en ESP32-P4 es **experimental** (I2C/WiFi según build); el bring-up vive en `apps/esp-32/` y el camino de producción es ESP-IDF (`esp_video`: CSI + ISP + JPEG/H264).
- Sin driver CSI en MicroPython: el firmware solo hace **probe SCCB** y telemetría; la captura real va por ESP-IDF o por el gateway (ver [decisiones de hardware](../../explanation/hardware-decisiones)).
