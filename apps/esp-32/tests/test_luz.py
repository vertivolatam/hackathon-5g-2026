"""Sensor BH1750 + iluminador nocturno, sin hardware.

FakeI2C responde a 0x23 con 2 bytes big-endian (lux * 1.2). Verifica:
conversión lux, umbral día/noche, update_light enciende/apaga el pin y
publica lux+night_light en la telemetría, y NACK no tumba nada.
Corre con `python3 apps/esp-32/tests/test_luz.py` (CPython).
"""
import sys
import types


class FakePin:
    def __init__(self, n):
        self.state = 0

    def on(self):
        self.state = 1

    def off(self):
        self.state = 0


class FakeI2C:
    def __init__(self, lux=None):
        self.lux = lux  # None = NACK
        self.writes = []

    def writeto(self, addr, buf):
        if self.lux is None or addr != 0x23:
            raise OSError("NACK")
        self.writes.append((addr, bytes(buf)))

    def readfrom(self, addr, n):
        if self.lux is None or addr != 0x23:
            raise OSError("NACK")
        raw = int(self.lux * 1.2)
        return bytes([(raw >> 8) & 0xFF, raw & 0xFF])[:n]


sys.path.insert(0, "apps/esp-32")

from drivers.luz import Bh1750, is_night  # noqa: E402
import main as mainmod  # noqa: E402

i2c = FakeI2C(lux=500.0)
assert abs(Bh1750(i2c).read_lux(sleep=lambda ms: None) - 500.0) < 1.0
assert i2c.writes[0] == (0x23, b"\x01")  # power on primero
assert i2c.writes[1] == (0x23, b"\x20")  # one-time alta resolución
assert is_night(0.5) is True
assert is_night(500.0) is False
assert is_night(10.0, threshold=10.0) is False  # borde: de día
try:
    Bh1750(FakeI2C(lux=None)).read_lux()
    raise AssertionError("debió fallar sin sensor")
except OSError:
    pass

# update_light con noche: enciende pin y publica en telemetría.
mainmod._night_pin = FakePin(47)
mainmod.update_light(FakeI2C(lux=0.0))
assert mainmod._night_pin.state == 1
assert mainmod._night is True
t = mainmod.read_sensors()
assert t["lux"] == 0.0 and t["night_light"] is True, t

# De día: apaga.
mainmod.update_light(FakeI2C(lux=20000.0))
assert mainmod._night_pin.state == 0
assert mainmod.read_sensors()["night_light"] is False

# Sin sensor: no tumba y conserva estado.
mainmod.update_light(FakeI2C(lux=None))
assert mainmod._night is False
print("luz OK: BH1750 + umbral + iluminador + telemetria")
