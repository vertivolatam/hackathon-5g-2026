# apps/esp-32 — ESP32-P4-NANO (MicroPython)

Firmware Python para **Waveshare ESP32-P4-NANO / WIFI6-DB**. Port 1:1 del
bring-up Rust original (`git log` previo a la migración): I2C0 400 kHz en
GPIO7/8, backlight 10.1" (0x45:0x96), GT911 polling (0x5D/0x14), probe
ES8311 (0x18) y SCCB de cámara. Más telemetría MQTT `agrivision/telemetry`
para el backend (ver `backend/` y `docs/vision-rf-detr.md`).

> Estado P4: MicroPython en ESP32-P4 es **experimental** (I2C/WiFi pueden
> fallar según build). Si la placa no trae soporte, el camino de
> producción sigue siendo ESP-IDF (display DSI, CSI, ETH, WiFi SDIO).
> Este código también corre en ESP32-S3/C3 con MicroPython estable.

## Archivos

| Archivo | Rol |
|---|---|
| `boot.py` | WiFi al arranque (lee `config.py`) |
| `main.py` | bring-up + loop touch + MQTT (port de `main.rs`) |
| `config.py` | WiFi/MQTT/trampa (editar antes de flashear) |
| `board.py` | pinout y direcciones (port de `board.rs`) |
| `drivers/backlight.py` | brillo 0..255 (port) |
| `drivers/es8311.py` | init playback + chip_id (port) |
| `drivers/gt911.py` | probe + polling 1er punto (port) |
| `drivers/camera.py` | probe SCCB OV5647/SC2336 (port) |
| `drivers/net.py` | contrato RMII + WiFi (port de `eth.rs`) |
| `drivers/display.py` | parámetros panel 800x1280 + nota DSI (port) |
| `tests/test_smoke.py` | smoke CI sin hardware |

## Mapa rápido

Igual que el README Rust original: I2C GPIO7/8; ES8311 `0x18`;
GT911 `0x5D`/`0x14` polling; backlight `0x45:0x96`; cámara SCCB
`0x36`/`0x30`; RMII en `drivers/net.py`; SDIO WiFi sin reclamar.

## Flashear (MicroPython)

```sh
# 1. firmware MicroPython para tu placa (micropython.org) vía esptool
# 2. copiar: boot.py main.py config.py board.py drivers/
#    (ampy/rshell/mpremote: `mpremote cp -r ... :`)
# 3. editar config.py (WiFi + MQTT_HOST del broker)
```

Salida esperada por serie (115200): `backlight ok`, `es8311 chip_id`,
`gt911 ok addr=0x5d (polling)` o NACKs accionables, `touch x=…` al tocar,
`mqtt ok` y publishes a `agrivision/telemetry`.

## CI

`firmware.yml`: `py_compile` + `tests/test_smoke.py` (I2C falso).
Sin toolchain Rust: el target `riscv32imafc` y `cargo` salieron del repo
con esta migración.
