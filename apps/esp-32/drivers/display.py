"""Display 10.1" 800x1280 (port de display_dsi.rs + display_mipidsi_spi.rs).

Realidad Python 2026: no existe driver MIPI-DSI serie en MicroPython.
Camino de producción: ESP-IDF + componente Waveshare
(`waveshare/esp_lcd_jd9365_10_1`), target esp32p4, con la secuencia DCS
del panel portada desde ese componente.

Este módulo conserva los parámetros del panel (timings placeholder:
medir del driver Waveshare antes de producción) y la nota del rol de
`mipidsi`: ese paquete solo habla MIPI Display Command Set sobre
SPI/paralelo GPIO ("MIPI Display Serial Interface is NOT supported"
según su propio README), útil como panel auxiliar de debug y como
referencia de modelado Model/Builder/InitSequence, nunca contra el
DSI serie 2-lane de 10.1".
"""
from board import DSI_LANES, LCD_H_ACTIVE, LCD_V_ACTIVE

# Paneles del Kit-D Waveshare: JD9365 (default) / ILI9881C / EK79007.
PANEL_DEFAULT = "JD9365"
# Bitrate del bus DSI del Kit-D 10.1" 2-lane (default upstream esp-hal).
DSI_LANE_RATE_MBPS = 500

# Timings placeholder del JD9365 a 60 MHz RGB565. Los porches/sync
# dependen del panel físico: medir del waveshare/esp_lcd_jd9365.
DPI_TIMING = {
    "h_active": LCD_H_ACTIVE,
    "hsw": 10,
    "hbp": 20,
    "hfp": 20,
    "v_active": LCD_V_ACTIVE,
    "vsw": 4,
    "vbp": 10,
    "vfp": 10,
    "pixel_clock_mhz": 60.0,
    "lanes": DSI_LANES,
}


def note():
    """Devuelve la nota de arquitectura del display en una línea.

    Returns:
        str: recordatorio de que `mipidsi` es command-set sobre
            SPI/paralelo y el DSI nativo va por ESP-IDF.
    """
    return "mipidsi=command-set-over-SPI/parallel; native-DSI-10.1in=ESP-IDF"
