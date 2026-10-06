//! Display nativo MIPI-DSI 2-lane (10.1" 800x1280).
//!
//! - Paneles Kit-D: JD9365 (default) / ILI9881C / EK79007 (Kconfig BSP).
//! - esp-hal `mipi_dsi` es `unstable` P4-only desde PR #5596 (jun-2026):
//!   `MipiDsi::new(dsi, vdma_ch, Config{ _2 lanes, 500 Mbps })`
//!   -> `dbi(vc)` para secuencia DCS de init -> `dpi(config, fbs)` streaming VDMA.
//! - Framebuffers: 1..=3 slices, `h*v*bpp` bytes, alineados 64B, EN PSRAM.
//! - Backlight NO es GPIO: I2C 0x45 reg 0x96 (ver backlight.rs).
//!
//! La secuencia DCS exacta del JD9365 vive en el componente ESP-IDF
//! `waveshare/esp_lcd_jd9365` (`idf.py add-dependency`). Portarla aquí es
//! copiar los `dcs_write(cmd, params)` al `DsiDbi` y respetar delays.
//! Este módulo compila solo con `--features dsi` para no exigir PSRAM
//! ni `unstable` en el bring-up I2C base.

#![cfg(feature = "dsi")]

use esp_hal::mipi_dsi::{
    dpi::{ColorFormat, DpiConfig, FrameTiming},
    Config,
};

/// 800x1280 RGB565. Los porches/sync dependen del panel (valores placeholder:
/// medir del driver `waveshare/esp_lcd_jd9365` antes de producción).
pub fn default_dpi_config(dpi_clk_src: esp_hal::mipi_dsi::dpi::DpiClockSource) -> DpiConfig {
    DpiConfig {
        virtual_channel: 0,
        pixel_clock_mhz: 60.0,
        dpi_clk_src,
        in_color_format: ColorFormat::Rgb565,
        out_color_format: ColorFormat::Rgb565,
        timing: FrameTiming {
            h_active: crate::board::LCD_H_ACTIVE as u32,
            hsw: 10,
            hbp: 20,
            hfp: 20,
            v_active: crate::board::LCD_V_ACTIVE as u32,
            vsw: 4,
            vbp: 10,
            vfp: 10,
        },
    }
}

pub fn default_bus_config() -> Config {
    // Default upstream = 2 lanes @ 500 Mbps, refclk XTAL, auto clock-lane.
    // Coincide con el Kit-D 10.1" 2-lane; si tu panel pide otro bitrate,
    // usa los builders `with_num_data_lanes()` / `with_lane_bit_rate_mbps()`
    // que genera `#[derive(BuilderLite)]`.
    Config::default()
}

// El flujo real (requiere singletons P4, omitido del build base):
//   let dsi = MipiDsi::new(peripherals.MIPI_DSI, peripherals.VDMA_CH0, default_bus_config())?;
//   let mut dbi = dsi.dbi(0);
//   jd9365_init(&mut dbi, &mut delay)?; // secuencia portada de waveshare/esp_lcd_jd9365
//   let dpi = dsi.dpi(default_dpi_config(clk_src), &fbs)?;
//   loop { render(&mut fb); dpi.wait_for_vsync(); }
