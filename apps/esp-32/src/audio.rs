//! ES8311 codec (I2C 0x18) + NS4150B (PA_CTRL GPIO53) + I2S P4.
//!
//! Solo control I2C aquí; el stream I2S (GPIO9..13) lo owns esp-hal::i2s.
//! Secuencia mínima: reset, clock, DAC power. Registro completo en datasheet.

use crate::board::ADDR_ES8311;
use embedded_hal::i2c::I2c;

pub struct Es8311<I2C> {
    i2c: I2C,
}

impl<I2C: I2c> Es8311<I2C> {
    pub fn new(i2c: I2C) -> Self {
        Self { i2c }
    }

    /// Init mínimo audible (speaker 8Ω 2W vía header MX1.25).
    /// El caller debe poner PA_CTRL=alto tras esto.
    pub fn init_playback(&mut self) -> Result<(), I2C::Error> {
        // Reset: reg 0x00 = 0x80, luego 0x00.
        self.i2c.write(ADDR_ES8311, &[0x00, 0x80])?;
        self.i2c.write(ADDR_ES8311, &[0x00, 0x00])?;
        // CLK manager: MCLK presente (GPIO13), BCLK 48kHz típico.
        self.i2c.write(ADDR_ES8311, &[0x01, 0x3F])?;
        // DAC on, PGA típico.
        self.i2c.write(ADDR_ES8311, &[0x12, 0x00])?;
        self.i2c.write(ADDR_ES8311, &[0x10, 0x1C])?;
        Ok(())
    }

    /// Lee CHIP_ID (reg 0xFD, esperado 0x83) para sanity-check del bus.
    pub fn chip_id(&mut self) -> Result<u8, I2C::Error> {
        let mut id = [0u8; 1];
        self.i2c.write_read(ADDR_ES8311, &[0xFD], &mut id)?;
        Ok(id[0])
    }
}
