"""Pinout canónico ESP32-P4-NANO / WIFI6-DB (port de board.rs).

Este módulo es la única fuente de verdad del hardware: pines GPIO,
direcciones I2C y parámetros del panel. Todos los drivers importan
sus constantes de aquí para no duplicar números mágicos.

Fuentes:
    - Waveshare wiki + docs.waveshare.com/ESP32-P4-NANO-WIFI6-DB
    - BSP espp `waveshare/esp32_p4_nano` (mapa RMII, bus I2C compartido)

Regla de oro:
    GPIO7=SDA y GPIO8=SCL forman el único bus I2C interno, compartido
    por ES8311 + GT911 + backlight 0x45 + SCCB de cámara. RST/INT del
    touch y RESET/XCLK de la cámara NO están ruteados en la NANO, por
    eso el touch trabaja por polling y la cámara en free-run.
"""

# ---------------------------------------------------------------------------
# Bus I2C interno compartido.
# ---------------------------------------------------------------------------
I2C_SDA_GPIO = 7
I2C_SCL_GPIO = 8
I2C_FREQ_HZ = 400_000

# ---------------------------------------------------------------------------
# Audio I2S hacia el codec ES8311 (solo referencia de cableado).
# MicroPython maneja el stream con machine.I2S por separado; el control
# del codec (volumen, rutas, power) va por I2C, ver drivers/es8311.py.
# ---------------------------------------------------------------------------
I2S_DOUT_GPIO = 9  # P4 -> codec DSDIN (playback)
I2S_WS_GPIO = 10  # LRCK / word select
I2S_DIN_GPIO = 11  # codec ASDOUT -> P4 (capture/mic)
I2S_SCLK_GPIO = 12
I2S_MCLK_GPIO = 13
# Enable del amplificador NS4150B. Activo alto: subir tras init_playback().
PA_CTRL_GPIO = 53

# ---------------------------------------------------------------------------
# SDIO WiFi6: ESP32-C5-MINI-1U (rev WIFI6-DB) o ESP32-C6-MINI-1 (NANO clásica).
# NO reclamar estos pines desde MicroPython: los usa el módulo de radio.
# ---------------------------------------------------------------------------
SDIO_D0_GPIO, SDIO_D1_GPIO, SDIO_D2_GPIO, SDIO_D3_GPIO = 14, 15, 16, 17
SDIO_CLK_GPIO, SDIO_CMD_GPIO = 18, 19
C5_CHIP_PU_GPIO = 54

# ---------------------------------------------------------------------------
# Ethernet RMII hacia el PHY IP101GRI (referencia de cableado).
# Sin driver RMII en MicroPython 2026: el bring-up real es ESP-IDF
# (esp_eth + PHY IP101). Ver drivers/net.py.
# ---------------------------------------------------------------------------
ETH_REF_CLK_GPIO = 50  # 50 MHz PHY -> P4
ETH_TX_EN_GPIO = 49
ETH_TXD0_GPIO, ETH_TXD1_GPIO = 34, 35  # GPIO35 es strapping: cuidado en boot
ETH_CRS_DV_GPIO = 28
ETH_RXD0_GPIO, ETH_RXD1_GPIO = 29, 30
ETH_MDC_GPIO, ETH_MDIO_GPIO = 31, 52
ETH_PHY_RST_GPIO = 51

# ---------------------------------------------------------------------------
# UART0 consola (Type-C). No usar como GPIO general.
# ---------------------------------------------------------------------------
UART_TX_GPIO, UART_RX_GPIO = 37, 38

# ---------------------------------------------------------------------------
# Direcciones I2C de 7 bits en el bus compartido.
# ---------------------------------------------------------------------------
ADDR_ES8311 = 0x18
ADDR_GT911_A = 0x5D  # dirección primaria del touch (probar primero)
ADDR_GT911_B = 0x14  # dirección alterna (algunas variantes del panel)
ADDR_BACKLIGHT = 0x45
REG_BACKLIGHT_BRIGHTNESS = 0x96

# ---------------------------------------------------------------------------
# Display 10.1" 800x1280, MIPI-DSI 2 lanes. Reset LCD no conectado.
# ---------------------------------------------------------------------------
LCD_H_ACTIVE = 800
LCD_V_ACTIVE = 1280
DSI_LANES = 2
