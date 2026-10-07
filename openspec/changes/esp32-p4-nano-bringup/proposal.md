# Proposal

## Why

La trampa inteligente de broca del café necesita un nodo de campo con cómputo en borde y un gateway 5G provisionable de forma repetible. Hoy el firmware de la placa de desarrollo ESP32-P4-NANO vive fuera del monorepo y el flasheo de la SD del gateway (Raspberry Pi 4 64-bit, balenaOS) depende de un link Etcher que no auto-abre en todas las estaciones. Este change mete ambos al repo con contratos verificables para el MVP del hackatón: 1 trampa → LoRa → gateway 5G → Edge/Nube → AgriVision.

## What Changes

- Nuevo crate `apps/esp-32` (`esp32-p4-nano-fw`, `no_std`, RISC-V): bring-up I2C compartido (GPIO7/8 @ 400 kHz), backlight 10.1" (0x45:0x96), touch GT911 en polling (0x5D/0x14), probe ES8311 (0x18) y SCCB de cámara; pipeline DSI nativo tras `--features dsi` (esp-hal `unstable`).
- Documentación del rol real de `mipidsi 0.10`: command-set sobre SPI/paralelo, NO DSI serie nativo; el DSI 10.1" (JD9365/ILI9881C/EK79007) va por `esp-hal::mipi_dsi`.
- Flujo de provisionamiento del gateway por balenaCLI (`balena/balena.sh` + `docker-compose.yml`): `os download` → `config generate` → `os configure` → `os initialize`, sin secretos en git.
- Especificación de dominio de la red de trampeo (trampa → LoRaWAN → gateway 5G → Edge/Nube → alertas) derivada de `business/` y de la inferencia visual de la sesión anterior.

## Capabilities

### New Capabilities

- `edge-firmware/esp32-p4-nano`: comportamiento observable del firmware de bring-up del nodo ESP32-P4-NANO (I2C, backlight, touch, audio-probe, cámara-probe, display-DSI).
- `edge-gateway/balena-provisioning`: provisionamiento repetible del gateway Raspberry Pi 4 64-bit con balenaOS vía balenaCLI.
- `field-monitoring/broca-trap-network`: red de monitoreo de broca (trampa Edge-AI → LoRaWAN → gateway 5G → Edge/Nube → mapa y alertas AgriVision).

### Modified Capabilities

Ninguna (repo sin specs previas).

## Impact

- Código: `apps/esp-32/**` (Rust), `balena/**` (shell + compose), `docs/esp32-p4-nano/**`, workflow `.github/workflows/firmware.yml`.
- Dependencias: `esp-hal 1.2` (`unstable` para DSI), `embedded-hal 1.0`, `embedded-hal-bus 0.3`, `mipidsi 0.10`; balenaCLI v25 en host/CI.
- Sistemas: gateway `raspberrypi4-64` (balenaOS 8.0.9+rev2, WiFi NOKIA-C80A); leaf ESP32-P4-NANO por USB/UART o Ethernet.
