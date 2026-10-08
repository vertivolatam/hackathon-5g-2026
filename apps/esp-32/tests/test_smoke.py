"""Smoke test de CI: drivers sin hardware.

Inyecta módulos `machine`/`network` falsos en sys.modules antes de
importar, con un FakeI2C que hace ACK selectivo por dirección. Verifica:
bytes exactos del backlight, chip_id del ES8311, parse del punto GT911,
probe SCCB positivo y negativo, y error propagado sin touch.
Además: dominios de potencia (on/off + settle), presupuesto diario en
Wh, desfase de wake determinista, y cliente AT del módem (registro,
RSSI, PDP) con UART programada, en positivo y negativo.
Corre con `python3 apps/esp-32/tests/test_smoke.py` (CPython, sin placa).
"""
import sys
import types


class FakePin:
    def __init__(self, n):
        self.n = n
        self.state = 0

    def on(self):
        self.state = 1

    def off(self):
        self.state = 0

    def value(self, v=None):
        if v is None:
            return self.state
        self.state = v


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
machine.Pin = FakePin
sys.modules["machine"] = machine
sys.modules["network"] = types.ModuleType("network")

sys.path.insert(0, "apps/esp-32")

from board import ADDR_BACKLIGHT, ADDR_ES8311  # noqa: E402
from drivers import camera  # noqa: E402
from drivers.backlight import Backlight  # noqa: E402
from drivers.es8311 import Es8311  # noqa: E402
from drivers.gt911 import Gt911  # noqa: E402
from drivers.modem import Modem  # noqa: E402
from drivers.power import PowerDomain, daily_energy_wh, wake_offset_s  # noqa: E402

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


class FakeUART:
    """UART programada: responde según el comando escrito."""

    def __init__(self, registered=True):
        self.registered = registered
        self.written = []
        self._queue = []

    def write(self, buf):
        cmd = bytes(buf).decode().strip()
        self.written.append(cmd)
        if cmd == "ATE1":
            self._queue = [b"ATE1\r\n", b"OK\r\n"]
        elif cmd == "AT+C5GREG?":
            stat = "1" if self.registered else "0"
            self._queue = [b"+C5GREG: 0,%s\r\n" % stat.encode(), b"OK\r\n"]
        elif cmd == "AT+CEREG?":
            self._queue = [b"+CEREG: 0,0\r\n", b"OK\r\n"]
        elif cmd == "AT+CSQ":
            self._queue = [b"+CSQ: 20,99\r\n", b"OK\r\n"]
        else:
            self._queue = [b"OK\r\n"]

    def readline(self):
        if self._queue:
            return self._queue.pop(0)
        return b""


# Potencia: dominio on/off, presupuesto y desfase.
sleeps = []
pin = FakePin(4)
dom = PowerDomain(pin, "modem", settle_ms=50)
dom.on(sleep=sleeps.append)
assert pin.state == 1 and sleeps == [50], (pin.state, sleeps)
dom.off()
assert pin.state == 0 and dom.is_on is False
e = daily_energy_wh()
assert 3.0 < e < 4.0, e  # ~3.3 Wh/día con ciclo 900/45/5
o1 = wake_offset_s("trap-01")
assert o1 == wake_offset_s("trap-01") and 0 <= o1 < 900, o1

# Módem: registro, RSSI y PDP en positivo y negativo.
mdm = Modem(FakeUART(registered=True), "internet")
assert mdm.alive() is True
assert mdm.registration() == ("NR", "1"), mdm.registration()
assert mdm.wait_registered(tries=1, sleep=lambda ms: None) is True
assert mdm.signal_dbm() == -73, mdm.signal_dbm()  # CSQ 20 -> -113+40
assert mdm.pdp_up() is True
assert any(c.startswith('AT+CGDCONT=1,"IPV4V6","internet"') for c in mdm._uart.written)
mdm2 = Modem(FakeUART(registered=False), "internet")
assert mdm2.wait_registered(tries=2, sleep=lambda ms: None) is False
print("smoke OK: power/modem (%.2f Wh/dia, offset trap-01=%ds)" % (e, o1))
