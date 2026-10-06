# Tasks

## 1. Firmware bring-up ESP32-P4-NANO

- [ ] 1.1 Módulos I2C (backlight 0x45, GT911 0x5D/0x14 polling, ES8311 0x18, SCCB probe) con patrón `new(i2c)` + `RefCellDevice`, verificar con `cargo check -p esp32-p4-nano-fw --target riscv32imafc-unknown-none-elf` sin errores
- [ ] 1.2 `main.rs` con loop de monitoreo y logs accionables (`backlight ok`, `chip_id`, `gt911 ok`/NACK, `touch x=…`), verificar por monitor serie a 115200 en placa real
- [ ] 1.3 `display_dsi.rs` tras `--features dsi` con `Config::default` (2 lanes @ 500 Mbps) y `DpiConfig` 800×1280 RGB565, verificar con `cargo check --features dsi` sin errores
- [ ] 1.4 Documentar rol de `mipidsi 0.10` (SPI/paralelo, no DSI nativo) en `display_mipidsi_spi.rs` y README, verificar que el README cite la limitación del crate

## 2. Gateway balena + monorepo

- [ ] 2.1 `balena/balena.sh` con flujo `os download → config generate → os configure → os initialize` fijando `raspberrypi4-64`/8.0.9+rev2/wifi, verificar con `bash -n` y revisión de que no hay secretos versionados
- [ ] 2.2 `balena/docker-compose.yml` (gateway + esp-provisioner con `espflash` y acceso serie), verificar con `docker compose config` válido
- [ ] 2.3 Pinmap `docs/esp32-p4-nano/pinmap.md` consistente con `src/board.rs` (GPIO7/8, RMII 28-35/49-52, SDIO 14-19/54, I2S 9-13/53), verificar por revisión cruzada tabla↔código
- [ ] 2.4 CI `firmware.yml` (check base + check `--features dsi` + fmt + clippy), verificar con `gh workflow view firmware` y run verde en el PR

## 3. Integración y validación en campo

- [ ] 3.1 Flashear SD del gateway con `balena.sh` (DRIVE=/dev/sdX confirmada vía `util available-drives`), verificar arranque balenaOS y aparición en el fleet
- [ ] 3.2 Flashear leaf ESP32-P4-NANO con `espflash` y validar logs de bring-up (backlight, touch, audio-probe, SCCB), verificar por salida serie
- [ ] 3.3 Medir timings DSI reales del JD9365 desde `waveshare/esp_lcd_jd9365` y sustituir placeholders de `FrameTiming`, verificar imagen estable en el 10.1"
- [ ] 3.4 Registrar decisiones de negocio pendientes (marca, gateway MVP, nodo fauna) en `business/` vía skill `problem-validation`, verificar con estado Espacio 1 actualizado
