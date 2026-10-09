"""Sensor de luz ambiental BH1750 por I2C (día/noche para la trampa).

La broca también cae de noche y la AR1335/OV5647 necesita luz: bajo
LUX_NIGHT_THRESHOLD se enciende la iluminación nocturna (LED blanco/IR
por MOSFET) y la trampa sigue capturando. De día se apaga para ahorrar
los ~3W del iluminador (ver potencia en drivers/power.py).

Protocolo BH1750 (dirección 0x23, o 0x5C según ADDR pin): Power ON
(0x01) + medida one-time alta resolución (0x20, 1 lx, ~180 ms) y leer
2 bytes big-endian: lux = raw / 1.2. Sin registros de configuración:
ideal para el bus compartido GPIO7/8.
"""

ADDR_DEFAULT = 0x23
CMD_POWER_ON = 0x01
CMD_ONE_TIME_HRES = 0x20
MEASURE_MS = 180

# Umbral día/noche en lux (noche cerrada <1 lx, interior ~50 lx,
# exterior nublado ~1.000 lx, sol directo >30.000 lx).
NIGHT_LUX_DEFAULT = 10.0


class Bh1750:
    """BH1750 en el bus I2C compartido (no lo cierra ni lo reconfigura).

    Args:
        i2c: bus machine.I2C ya inicializado a 400 kHz.
        addr: dirección 7-bit (0x23 default, 0x5C alterna).
    """

    def __init__(self, i2c, addr=ADDR_DEFAULT):
        self._i2c = i2c
        self._addr = addr

    def read_lux(self, sleep=None):
        """Una medida one-time en lux. Lanza OSError si NACK/timeout."""
        self._i2c.writeto(self._addr, bytes([CMD_POWER_ON]))
        self._i2c.writeto(self._addr, bytes([CMD_ONE_TIME_HRES]))
        if sleep is not None:
            sleep(MEASURE_MS)
        raw = bytes(self._i2c.readfrom(self._addr, 2))
        if len(raw) != 2:
            raise OSError("BH1750 lectura corta")
        return ((raw[0] << 8) | raw[1]) / 1.2


def is_night(lux, threshold=NIGHT_LUX_DEFAULT):
    """True si hay que encender iluminación (lux bajo umbral)."""
    return lux < threshold
