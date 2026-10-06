//! Pinout canónico ESP32-P4-NANO / WIFI6-DB (Waveshare wiki + docs.waveshare.com).
//!
//! Fuentes:
//! - https://docs.waveshare.com/ESP32-P4-NANO-WIFI6-DB (tabla GPIO Allocation)
//! - https://www.waveshare.com/wiki/ESP32-P4-Nano-StartPage
//! - espp BSP `waveshare/esp32_p4_nano` (RMII map, I2C bus compartido)
//!
//! Regla de oro: GPIO7=SDA, GPIO8=SCL compartidos por ES8311 + GT911 +
//! backlight 0x45 + SCCB cámara. RST/INT de touch y RESET/XCLK de cámara
//! NO están ruteados -> polling, sin reset por GPIO.

/// Bus I2C interno compartido (embedded-hal).
pub const I2C_SDA_GPIO: u8 = 7;
pub const I2C_SCL_GPIO: u8 = 8;

/// Audio I2S -> ES8311.
pub const I2S_DOUT_GPIO: u8 = 9; // P4 -> codec DSDIN (playback)
pub const I2S_WS_GPIO: u8 = 10; // LRCK
pub const I2S_DIN_GPIO: u8 = 11; // codec ASDOUT -> P4 (capture/mic)
pub const I2S_SCLK_GPIO: u8 = 12;
pub const I2S_MCLK_GPIO: u8 = 13;
/// Enable amplificador NS4150B. Activo alto.
pub const PA_CTRL_GPIO: u8 = 53;

/// SDIO WiFi6: ESP32-C5-MINI-1U (rev WIFI6-DB) o ESP32-C6-MINI-1 (rev NANO clásica).
/// D0..D3=GPIO14..17, CLK=GPIO18, CMD=GPIO19, C5_IO02=GPIO6, EN=GPIO54.
pub const SDIO_D0_GPIO: u8 = 14;
pub const SDIO_D1_GPIO: u8 = 15;
pub const SDIO_D2_GPIO: u8 = 16;
pub const SDIO_D3_GPIO: u8 = 17;
pub const SDIO_CLK_GPIO: u8 = 18;
pub const SDIO_CMD_GPIO: u8 = 19;
pub const C5_CHIP_PU_GPIO: u8 = 54;

/// Ethernet RMII -> IP101GRI (interno EMAC P4).
pub const ETH_REF_CLK_GPIO: u8 = 50; // 50MHz PHY->P4
pub const ETH_TX_EN_GPIO: u8 = 49;
pub const ETH_TXD0_GPIO: u8 = 34;
pub const ETH_TXD1_GPIO: u8 = 35; // strapping, cuidado en boot
pub const ETH_CRS_DV_GPIO: u8 = 28;
pub const ETH_RXD0_GPIO: u8 = 29;
pub const ETH_RXD1_GPIO: u8 = 30;
pub const ETH_MDC_GPIO: u8 = 31;
pub const ETH_MDIO_GPIO: u8 = 52;
pub const ETH_PHY_RST_GPIO: u8 = 51;

/// microSD 4-bit SDMMC.
pub const SD_D0_GPIO: u8 = 39;
pub const SD_D1_GPIO: u8 = 40;
pub const SD_D2_GPIO: u8 = 41;
pub const SD_D3_GPIO: u8 = 42;
pub const SD_CLK_GPIO: u8 = 43;
pub const SD_CMD_GPIO: u8 = 44;
pub const SD_VDD_EN_GPIO: u8 = 45; // bajo = enable. No usar como GPIO si hay TF.

/// UART0 consola (Type-C). No usar como GPIO general.
pub const UART_TX_GPIO: u8 = 37;
pub const UART_RX_GPIO: u8 = 38;

/// Direcciones I2C 7-bit (embedded-hal SevenBitAddress por defecto).
pub const ADDR_ES8311: u8 = 0x18;
pub const ADDR_GT911_A: u8 = 0x5D;
pub const ADDR_GT911_B: u8 = 0x14;
pub const ADDR_BACKLIGHT: u8 = 0x45;
pub const REG_BACKLIGHT_BRIGHTNESS: u8 = 0x96;

/// Display 10.1" 800x1280, MIPI-DSI 2-lane (Kit-D). Variantes: JD9365 /
/// ILI9881C / EK79007 según Kconfig del BSP. Reset LCD no conectado.
pub const LCD_H_ACTIVE: u16 = 800;
pub const LCD_V_ACTIVE: u16 = 1280;
pub const DSI_LANES: u8 = 2;
