//! Backlight 10.1" via I2C 0x45, registro 0x96.
//!
//! Patrón embedded-hal 1.0 (`embedded_hal::i2c::I2c`, SevenBitAddress por
//! defecto). El driver toma el bus por valor (`new(i2c)`), no `&mut`,
//! para seguir siendo compatible con bus compartido
//! (`embedded-hal-bus::i2c::RefCellDevice`).

use crate::board::{ADDR_BACKLIGHT, REG_BACKLIGHT_BRIGHTNESS};
use embedded_hal::i2c::I2c;

pub struct Backlight<I2C> {
    i2c: I2C,
}

impl<I2C: I2c> Backlight<I2C> {
    pub fn new(i2c: I2C) -> Self {
        Self { i2c }
    }

    /// brightness 0..=255. En JD9365 escribe el duty del controlador.
    /// En otros paneles el valor se guarda pero no aplica a HW (ver BSP espp).
    pub fn set_brightness(&mut self, brightness: u8) -> Result<(), I2C::Error> {
        self.i2c
            .write(ADDR_BACKLIGHT, &[REG_BACKLIGHT_BRIGHTNESS, brightness])
    }

    pub fn free(self) -> I2C {
        self.i2c
    }
}
