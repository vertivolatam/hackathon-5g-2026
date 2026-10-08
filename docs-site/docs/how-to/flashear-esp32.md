---
sidebar_position: 3
---

# Flashear el ESP32

Firmware en `apps/esp-32/` (MicroPython). Detalle de drivers y CI en su README.

```bash
# 1. Firmware MicroPython para tu placa vía esptool (micropython.org)
# 2. Editar apps/esp-32/config.py (WiFi + MQTT_HOST del broker)
# 3. Copiar al device (ej: mpremote cp -r boot.py main.py config.py board.py drivers/ :)
# 4. Serie 115200: espera `backlight ok`, `es8311 chip_id`, `gt911 ok`, `mqtt ok`
```

Nota: MicroPython en ESP32-P4-NANO es experimental. Si I2C/WiFi falla, el camino de producción es ESP-IDF (ver README de `apps/esp-32`).

## Vía Balena (flota, sin tocar la trampa)

El servicio `esp-provisioner` (`balena/docker-compose.yml`) lleva `espflash` + `mpremote`: con `balena push` el gateway recibe el firmware y flashea el leaf ESP32-P4-NANO por USB/UART, o copia MicroPython (`mpremote cp -r ... :`). Mismo flujo para updates: nuevo release en el fleet → el provisionador reflashea sin visita a campo.
