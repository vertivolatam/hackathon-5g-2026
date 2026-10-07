# Pinmap ESP32-P4-NANO / WIFI6-DB (fuentes: Waveshare wiki, docs.waveshare.com, BSP espp)

I2C0 compartido: SDA GPIO7 + SCL GPIO8 @ 400 kHz.
ES8311 (0x18) + GT911 (0x5D/0x14, polling, RST/INT NC) + backlight (0x45 reg 0x96) + SCCB cámara.

| GPIO | Señal | Conectado a | Notas |
|---|---|---|---|
| 6 | C5_IO02 / expansión | ESP32-C5-MINI-1U IO02 | No reclamar si hay WiFi6 |
| 7 | I2C SDA | ES8311, GT911, BL 0x45, SCCB, header | Bus compartido |
| 8 | I2C SCL | idem | Bus compartido |
| 9 | I2S DOUT | ES8311 DSDIN | Playback P4→codec |
| 10 | I2S WS | ES8311 LRCK | Frame sync |
| 11 | I2S DIN | ES8311 ASDOUT | Capture/mic |
| 12 | I2S SCLK | ES8311 SCLK | Bit clock |
| 13 | I2S MCLK | ES8311 MCLK | Master clock |
| 14-17 | SDIO D0..D3 | C5/C6 SDIO | WiFi6/BLE, no tocar |
| 18 | SDIO CLK | C5/C6 | |
| 19 | SDIO CMD | C5/C6 | |
| 20-23 | GPIO header | pads libres | 2×13 header |
| 24-27 | GPIO / USB1P1 | header | Func. mux USB |
| 28 | RMII CRS_DV | IP101GRI | ETH in |
| 29 | RMII RXD0 | IP101GRI | ETH in |
| 30 | RMII RXD1 | IP101GRI | ETH in |
| 31 | SMI MDC | IP101GRI | ETH mgmt clk (out) |
| 32-33 | GPIO header | pads libres | |
| 34 | RMII TXD0 | IP101GRI | ETH out |
| 35 | RMII TXD1 / BOOT | IP101GRI | **Strapping**: cuidado en reset |
| 36 | GPIO header (pull-up 3V3) | pad libre | Strapping |
| 37 | UART0 TXD | Type-C consola | No uso general |
| 38 | UART0 RXD | Type-C consola | No uso general |
| 39-42 | SD D0..D3 | TF slot SDIO3.0 | 4-bit |
| 43 | SD CLK | TF slot | |
| 44 | SD CMD | TF slot | |
| 45 | SD_VDD_EN / header | TF power | Bajo=enable; no GPIO con TF |
| 46-48 | GPIO header | pads libres | |
| 49 | RMII TX_EN | IP101GRI | ETH out |
| 50 | RMII REF_CLK | IP101GRI | 50 MHz PHY→P4 (in) |
| 51 | PHY RST | IP101GRI | GPIO out |
| 52 | SMI MDIO | IP101GRI | Bidireccional |
| 53 | PA_CTRL / header | NS4150B enable | Alto=amp on; no GPIO con audio |
| 54 | C5_CHIP_PU / header | C5 enable | Alto=on, bajo=reset |
| 0-5 | GPIO header | pads / XTAL_32K (0,1) | 0/1: quitar R32/R36 para GPIO |

Display: MIPI-DSI 2-lane, `LCD_RST` NC, backlight por I2C 0x45:0x96.
Touch: GT911 polling (INT/RST NC). Cámara: MIPI-CSI 2-lane, XCLK/RESET NC.
USB: Type-C (power/flash/debug) + Type-A OTG 2.0 HS. PoE: header dedicado.
Audio: mic SMD onboard + speaker MX1.25 8Ω 2W. RTC: header batería recargable.
