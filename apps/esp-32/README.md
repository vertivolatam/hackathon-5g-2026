# apps/esp-32 — ESP32-P4-NANO (Rust no_std)

Firmware para **Waveshare ESP32-P4-NANO / WIFI6-DB**:
`ESP32-P4NRW32X` (RISC-V dual-core + LP, 32 MB PSRAM, 16 MB flash) +
módulo SDIO WiFi6/BLE (`ESP32-C5-MINI-1U` en rev WIFI6-DB,
`ESP32-C6-MINI-1` en rev NANO clásica) +
MIPI-DSI 2-lane 10.1" 800×1280 + MIPI-CSI 2-lane +
USB OTG HS + RJ45 100M (IP101GRI) + PoE header + ES8311 + GT911 + TF SDIO3.0.

Target: `riscv32imafc-unknown-none-elf`. Verificado con
`cargo check -p esp32-p4-nano-fw --target riscv32imafc-unknown-none-elf`.

## Mapa rápido (fuente: Waveshare wiki + docs.waveshare.com/ESP32-P4-NANO-WIFI6-DB + BSP espp)

| Función | Pines / addr |
|---|---|
| I2C compartido SDA/SCL | GPIO7 / GPIO8, 400 kHz |
| Audio ES8311 | I2C `0x18`, I2S DOUT 9 / WS 10 / DIN 11 / SCLK 12 / MCLK 13, PA_CTRL 53 (alto) |
| Touch GT911 | I2C `0x5D`/`0x14`, **polling** (RST/INT NC) |
| Backlight 10.1" | I2C `0x45`, reg `0x96`, 0..255 (JD9365; otros paneles: stored-no-op) |
| Cámara CSI + SCCB | MIPI 2-lane, SCCB en GPIO7/8, XCLK/RESET NC (free-run). OV5647 `0x36`, SC2336 `0x30` |
| Display DSI | MIPI 2-lane, `LCD_RST` NC. Paneles: JD9365 / ILI9881C / EK79007 |
| Ethernet RMII | REF_CLK 50, TX_EN 49, TXD0 34, TXD1 35 (strapping), CRS_DV 28, RXD0 29, RXD1 30, MDC 31, MDIO 52, RST 51 |
| SDIO WiFi6 | D0..D3 14..17, CLK 18, CMD 19, EN 54 |
| TF SDMMC 4-bit | D0..D3 39..42, CLK 43, CMD 44, VDD_EN 45 (bajo=on) |
| Consola | UART0 TX 37 / RX 38 (Type-C). BOOT+RESET = download mode |

Detalle completo: `src/board.rs` (contrato) + `docs/esp32-p4-nano/pinmap.md`.

## Crates pedidos

- `embedded-hal 1.0.0` (`embedded_hal::i2c::I2c`, `SevenBitAddress` por defecto):
  `write`, `write_read`, `transaction`. Patrón: driver toma `I2C` por valor
  en `new()`, nunca `&mut` por método; el bus compartido se parte con
  `embedded-hal-bus 0.3` (`RefCellDevice::new(&bus)`). Ver `main.rs`,
  `backlight.rs`, `touch.rs`, `audio.rs`.
- `mipidsi 0.10.0`: **solo** MIPI Display Command Set sobre **SPI/paralelo**
  (`SpiInterface` + `Builder::new(Model, di).reset_pin(rst).init(&mut delay)`).
  El propio crate advierte: *"MIPI Display Serial Interface is NOT supported"*.
  Aquí se usa para (a) panel SPI auxiliar y (b) referencia de modelado
  `Model/Builder/InitSequence` al portar la init JD9365 al DSI nativo.
  Ver `src/display_mipidsi_spi.rs`. No instanciar contra el DSI 10.1".

## Display 10.1" nativo (dos caminos)

**A. Producción (recomendado): ESP-IDF + componente Waveshare.**
`idf.py add-dependency "waveshare/esp_lcd_jd9365_10_1"` (o `waveshare/esp_lcd_jd9365`
según panel), target `esp32p4`, flash+monitor. Incluye DSI video-mode, LVGL,
GT911, `esp_video` para CSI, `esp_eth`+IP101 para Ethernet. Referencia:
`components.espressif.com/components/waveshare/esp32_p4_nano`.

**B. Rust bare-metal (experimental, este crate, `--features dsi`):**
`esp-hal 1.2` (`unstable`) `MipiDsi::new(dsi, vdma_ch, Config{ _2 lanes, 500 Mbps })`
→ `dbi(vc)` secuencia DCS portada del componente Waveshare →
`dpi(DpiConfig{800×1280, Rgb565, Burst}, fbs)` con 1–3 framebuffers en PSRAM,
64 B alineados. Ver `src/display_dsi.rs`. Requiere panel 2-lane y PSRAM.
Estado upstream: PR esp-rs/esp-hal#5596 mergeado jun-2026 (P4-only, parcial).

## Cámara / WiFi6 / Ethernet en Rust

- CSI/ISP (`esp_video`/V4L2, JPEG/H264 1080p30): **sin driver esp-hal en 2026**.
  Este crate solo hace `probe_sccb()` (`src/camera.rs`). Producción = ESP-IDF.
- WiFi6 vía C5/C6 por SDIO: sin driver SDIO-hosted maduro en `no_std` Rust;
  producción = ESP-IDF (`esp_hosted` / SDIO slave). El `main.rs` no reclama
  GPIO14..19/54 para no pisar el módulo de radio.
- Ethernet RMII: contrato de pines en `src/eth.rs`; bring-up de referencia
  en ESP-IDF (`esp_eth` + PHY IP101). No se inicializa en el bring-up I2C base.

## Build / flash

```sh
rustup target add riscv32imafc-unknown-none-elf
cargo install espflash
cargo check -p esp32-p4-nano-fw --target riscv32imafc-unknown-none-elf
cargo run -p esp32-p4-nano-fw --release --target riscv32imafc-unknown-none-elf
# --features dsi  # solo con panel 2-lane + PSRAM, ver display_dsi.rs
```

Salida esperada por USB-JTAG (115200): `backlight ok`, `es8311 chip_id`,
`gt911 ok addr=0x5d (polling)` o NACKs accionables, `touch x=…` al tocar.

## Relación con balena (gateway RPi4-64 + leaf P4)

La P4-NANO no es device-type balena; el gateway es `raspberrypi4-64`
(balenaOS `8.0.9+rev2`, wifi `NOKIA-C80A`, dev-mode). La P4 cuelga por
USB/UART o Ethernet y el gateway la flashea/provisiona. Ver `balena/`:
`docker-compose.yml` (gateway + `espflash` service), `balena.sh`
(`os download`, `config generate`, `os configure`, `os initialize` /
`device init`, `local flash`, `util available-drives`) según
`docs.balena.io/reference/balena-cli/latest`. El link `efp.balena.io/open-image-url`
no auto-abrió Etcher en tu sesión: usa el CLI (comando exacto en `balena/balena.sh`).
