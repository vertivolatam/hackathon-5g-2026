# Design

## Context

Ver `proposal.md` (Why). Estado actual: el crate `apps/esp-32` ya compila (`cargo check --target riscv32imafc-unknown-none-elf`, base y `--features dsi`) con `esp-hal 1.2`, `embedded-hal 1.0`, `embedded-hal-bus 0.3`, `mipidsi 0.10`; `balena/balena.sh` implementa el flujo CLI. El dominio viene de `business/` (BioAgro 5G / RuralIA, broca del café, topología LoRaWAN→5G). Restricciones: ESP32-P4 sin radio (WiFi6 vía módulo SDIO C5/C6), DSI nativo solo en `esp-hal::mipi_dsi` (`unstable`, merge jun-2026), RST/INT táctil y XCLK/RESET de cámara no ruteados, `mipidsi` no habla DSI serie.

## Goals / Non-Goals

- Goals: bring-up I2C verificable por log; DSI nativo aislado tras feature; provisionamiento balena repetible sin secretos en git; dominio de monitoreo como specs vivas.
- Non-Goals: pipeline de visión CSI/ISP en Rust; driver SDIO WiFi6 en `no_std`; backend de RuralIA y app móvil (viven en `bio-trap/` y fases 6-8 del business).

## Decisions

- **esp-hal bare-metal sobre ESP-IDF para el bring-up**: el bring-up I2C/touch/backlight no necesita OS; ESP-IDF queda como camino de producción para DSI+CSI+WiFi+Ethernet (componentes `waveshare/esp_lcd_jd9365`, `esp_video`, `esp_eth`, `esp_hosted`). Alternativa (todo ESP-IDF desde el día 1) descartada: pierde el contrato Rust verificable en CI y el type-safety de `embedded-hal`.
- **`embedded-hal-bus::RefCellDevice` para el bus compartido**: patrón recomendado por docs.rs embedded-hal 1.0 (HAL expone exclusivo, el usuario parte). Alternativa `MutexDevice`/duplicar buses descartada: más RAM y riesgo de transacciones partidas entre ES8311/GT911/backlight/SCCB.
- **`mipidsi` solo como referencia + panel SPI auxiliar**: su `Builder/Model/InitSequence` modela cómo portar la init JD9365 al `DsiDbi` nativo. Alternativa (usar `mipidsi` contra el DSI 10.1") descartada: el crate declara no soportar DSI serie.
- **DSI tras `--features dsi` con `DpiConfig` explícito**: evita exigir PSRAM y `unstable` en el build base/CI. Campos validados contra `esp-hal 1.2.2` (`Config::default` = 2 lanes @ 500 Mbps; `DpiConfig{virtual_channel, pixel_clock_mhz, dpi_clk_src, in/out_color_format, timing}`).
- **balenaCLI en vez del link Etcher**: `efp.balena.io/open-image-url` no auto-abrió Etcher en la estación del equipo; el CLI es scripteable y auditable. `balena.sh` exige secretos por entorno.

## Risks / Trade-offs

- [Risk] Timings DSI del JD9365 (porches/sync) como placeholder → Mitigación: medir del componente Waveshare antes de producción; el panel puede no sincronizar hasta entonces.
- [Risk] `esp-hal::mipi_dsi` aún parcial (P4-only, `unstable`) → Mitigación: feature-gate + camino ESP-IDF documentado en `apps/esp-32/README.md`.
- [Risk] GPIO35 (TXD1) es strapping y SD_VDD_EN/PA_CTRL comparten header → Mitigación: pinmap en `docs/esp32-p4-nano/pinmap.md` y no reclamar esos GPIO en firmware hasta el bring-up Ethernet/audio.
- [Risk] Inconsistencias de negocio (marca BioAgro/BioTrap/RuralIA, Raymond/Reymond, gateway del MVP) → Mitigación: registradas como supuestos en `business/00-fuentes-visuales/inferencia-imagenes.md`; no bloquean el MVP técnico.

## Migration Plan

1. Merge de este change (monorepo + specs, sin comportamiento productivo previo que migrar).
2. En campo: flashear SD con `balena.sh`, arrancar gateway, `espflash` del `apps/esp-32` al leaf por USB.
3. Rollback: re-flasheo de SD/imagen anterior; el leaf vuelve al firmware previo por `espflash`.

## Open Questions

Ninguna que cambie specs, enfoque o tasks. Las 6 preguntas de negocio (marca, gateway MVP, nodo fauna, conectividad demo, costos/energía) se resuelven en Espacio 1 con el skill `problem-validation`, no aquí.
