//! Cámara MIPI-CSI 2-lane (OV5647 / SC2336, conector estilo RPi).
//!
//! Estado Rust (2026): esp-hal NO tiene driver CSI/ISP/V4L2. El pipeline
//! oficial es ESP-IDF `esp_video` (CSI receiver + ISP + JPEG/H264).
//! Este módulo deja el contrato SCCB (I2C GPIO7/8, XCLK/RESET no conectados,
//! sensor free-run) y un stub para no bloquear el build.

use embedded_hal::i2c::I2c;

/// Escanea la dirección SCCB del módulo montado (depende del vendor).
/// Devuelve la primera que hace ACK a un `write_read` de 1 byte.
pub fn probe_sccb<I2C: I2c>(i2c: &mut I2C, candidates: &[u8]) -> Option<u8> {
    for &addr in candidates {
        let mut b = [0u8; 1];
        if i2c.write_read(addr, &[0x00], &mut b).is_ok() {
            return Some(addr);
        }
    }
    None
}

/// Candidatos típicos: OV5647 0x36, SC2336 0x30.
pub const SCCB_CANDIDATES: &[u8] = &[0x36, 0x30, 0x3C];
