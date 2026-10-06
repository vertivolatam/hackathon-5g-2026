//! GT911 táctil capacitivo en modo polling.
//!
//! RST/INT no ruteados en la NANO -> no hay reset ni IRQ, se polea.
//! Prueba 0x5D y luego 0x14 (ambas documentadas por Waveshare).

use crate::board::{ADDR_GT911_A, ADDR_GT911_B};
use embedded_hal::i2c::I2c;

const REG_STATUS: u16 = 0x814E;
const REG_TOUCH1_X: u16 = 0x8150;

#[derive(Debug, Clone, Copy)]
pub struct TouchPoint {
    pub x: u16,
    pub y: u16,
    pub size: u8,
}

pub struct Gt911<I2C> {
    i2c: I2C,
    addr: u8,
}

impl<I2C: I2c> Gt911<I2C> {
    /// Prueba 0x5D y 0x14 leyendo el registro de estado. Devuelve error si
    /// ningún ACK responde (típico: flat cable del display suelto).
    pub fn new(mut i2c: I2C) -> Result<Self, I2C::Error> {
        for &addr in &[ADDR_GT911_A, ADDR_GT911_B] {
            let reg = REG_STATUS.to_be_bytes();
            let mut buf = [0u8; 1];
            if i2c.write_read(addr, &reg, &mut buf).is_ok() {
                return Ok(Self { i2c, addr });
            }
        }
        // Último intento para propagar el error real:
        let reg = REG_STATUS.to_be_bytes();
        let mut buf = [0u8; 1];
        i2c.write_read(ADDR_GT911_A, &reg, &mut buf)?;
        unreachable!()
    }

    pub fn address(&self) -> u8 {
        self.addr
    }

    /// Lee 1er punto. `Ok(None)` = sin dedo. Limpia flag escribiendo 0.
    pub fn read_first_point(&mut self) -> Result<Option<TouchPoint>, I2C::Error> {
        let mut status = [0u8; 1];
        self.i2c
            .write_read(self.addr, &REG_STATUS.to_be_bytes(), &mut status)?;
        if status[0] & 0x80 == 0 || status[0] & 0x0F == 0 {
            return Ok(None);
        }
        let mut raw = [0u8; 6];
        self.i2c
            .write_read(self.addr, &REG_TOUCH1_X.to_be_bytes(), &mut raw)?;
        let x = u16::from_le_bytes([raw[0], raw[1]]);
        let y = u16::from_le_bytes([raw[2], raw[3]]);
        let size = raw[4];
        // clear buffer-ready flag
        let _ = self.i2c.write(self.addr, &[0x81, 0x4E, 0x00]);
        Ok(Some(TouchPoint { x, y, size }))
    }
}
