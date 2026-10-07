"""Smoke test de CI: drivers sin hardware.

Inyecta módulos `machine`/`network` falsos en sys.modules antes de
importar, con un FakeI2C que hace ACK selectivo por dirección. Verifica:
bytes exactos del backlight, chip_id del ES8311, parse del punto GT911,
probe SCCB positivo y negativo, y error propagado sin touch.
Corre con `python3 apps/esp-32/tests/test_smoke.py` (CPython, sin placa).
"""
import sys
import types


class FakeI2C:
    def __init__(self, ack=None):
        self.ack = ack if ack is not None else set()
        self.writes = []

    def scan(self):
        return sorted(self.ack)

    def writeto(self, addr, buf):
        if addr not in self.ack:
            raise OSError("NACK")
        self.writes.append((addr, bytes(buf)))

    def writeto_mem(self, addr, mem, buf):
        self.writeto(addr, bytes([mem >> 8, mem & 0xFF]) + bytes(buf))

    def readfrom_mem(self, addr, mem, n):
        if addr not in self.ack:
            raise OSError("NACK")
        if mem == 0x814E:  # GT911 status: buffer ready + 1 toque
            return bytes([0x81])
        if mem == 0x8150:
            return bytes([100, 0, 50, 0, 9, 0])[:n]
        if mem == 0xFD:  # ES8311 chip id
            return bytes([0x83])[:n]
        return bytes(n)


machine = types.ModuleType("machine")
machine.I2C = FakeI2C
machine.Pin = lambda n: n
sys.modules["machine"] = machine
sys.modules["network"] = types.ModuleType("network")

sys.path.insert(0, "apps/esp-32")

from board import ADDR_BACKLIGHT, ADDR_ES8311  # noqa: E402
from drivers import camera  # noqa: E402
from drivers.backlight import Backlight  # noqa: E402
from drivers.es8311 import Es8311  # noqa: E402
from drivers.gt911 import Gt911  # noqa: E402

i2c = FakeI2C(ack={ADDR_BACKLIGHT, ADDR_ES8311, 0x5D, 0x36})
Backlight(i2c).set_brightness(200)
assert i2c.writes[0] == (0x45, bytes([0x96, 200])), i2c.writes
assert Es8311(i2c).chip_id() == 0x83
gt = Gt911.probe(i2c)
assert gt.address == 0x5D, gt.address
pt = gt.read_first_point()
assert (pt.x, pt.y, pt.size) == (100, 50, 9), pt
assert camera.probe_sccb(i2c) == 0x36
assert camera.probe_sccb(FakeI2C(ack=set())) is None
try:
    Gt911.probe(FakeI2C(ack=set()))
    raise AssertionError("debió fallar sin touch")
except OSError:
    pass
print("smoke OK: backlight/es8311/gt911/camera")
