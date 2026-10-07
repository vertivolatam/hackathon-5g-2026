"""Backlight del display 10.1" vía I2C (port de backlight.rs).

El brillo NO es un GPIO: lo maneja el controlador del panel por I2C
(dirección 0x45, registro 0x96). En paneles JD9365 el valor escribe el
duty del controlador; en otros paneles del Kit-D el valor se guarda
pero no aplica al hardware (stored-no-op, ver BSP espp).
"""
from board import ADDR_BACKLIGHT, REG_BACKLIGHT_BRIGHTNESS


class Backlight:
    """Control de brillo del panel por I2C.

    Args:
        i2c: bus I2C ya inicializado (machine.I2C). Se comparte con el
            resto de periféricos; esta clase nunca lo cierra ni lo
            reconfigura.
    """

    def __init__(self, i2c):
        """Guarda la referencia al bus compartido (sin tomar ownership)."""
        self.i2c = i2c

    def set_brightness(self, brightness):
        """Fija el brillo del panel.

        Args:
            brightness: nivel de 0 (apagado) a 255 (máximo). El bring-up
                usa 200 (~80%) como valor diurno legible sin saturar.

        Raises:
            ValueError: si brightness está fuera de 0..255.
            OSError: si el controlador no responde (NACK). Causa típica:
                flat MIPI-DSI suelto o panel sin 5V.
        """
        if not 0 <= brightness <= 255:
            raise ValueError("brightness 0..255")
        self.i2c.writeto(ADDR_BACKLIGHT, bytes([REG_BACKLIGHT_BRIGHTNESS, brightness]))
