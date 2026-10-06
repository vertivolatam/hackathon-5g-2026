//! Qué rol juega `mipidsi` 0.10.0 en este repo (pedido explícito del usuario).
//!
//! - `mipidsi::Builder` + `models::*` (ST7789/ST7735/ILI9341/ILI9486/GC9A01/...)
//!   manejan pantallas con **MIPI Display Command Set sobre SPI o paralelo GPIO**
//!   vía `display-interface::{SpiInterface, ParallelInterface}`.
//! - La cita del crate: *"MIPI Display Serial Interface is NOT supported"*.
//!   O sea: NO maneja el DSI serie nativo 2-lane del P4 / 10.1".
//! - Uso correcto aquí:
//!   (a) panel SPI auxiliar (debug) con el mismo `embedded-hal::i2c/spi` mindset,
//!   (b) referencia de cómo modelar `Model + Builder + InitSequence` para
//!       portar la init JD9365 al `DsiDbi` nativo (ver display_dsi.rs).
//!
//! Ejemplo canónico del crate (para un SPI display, no el DSI 10.1"):
//! ```ignore
//! use mipidsi::{Builder, models::ILI9486Rgb666};
//! use display_interface_spi::SpiInterface;
//! let mut buf = [0u8; 512];
//! let di = SpiInterface::new(spi, dc, &mut buf);
//! let mut disp = Builder::new(ILI9486Rgb666, di).reset_pin(rst).init(&mut delay)?;
//! use embedded_graphics::{pixelcolor::Rgb666, prelude::*};
//! disp.clear(Rgb666::BLACK)?;
//! ```
//!
//! Dependencia ya declarada en Cargo.toml (`mipidsi 0.10`, `embedded-graphics-core 0.4`).
//! No se instancia en `main.rs` para no exigir un bus SPI que la NANO usa en
//! flash/PSRAM; este archivo es contrato + doc viva.

pub fn note() -> &'static str {
    "mipidsi=command-set-over-SPI/parallel; native-DSI-10.1in=esp-hal::mipi_dsi"
}
