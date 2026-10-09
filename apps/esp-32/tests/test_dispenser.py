"""Bomba EZO-PMP + dosificador horario, sin hardware.

FakeI2C emula el protocolo Atlas: comando ASCII por writeto, espera de
300 ms y lectura con código (1 ok + payload). Verifica: ping, D,ml con
bytes exactos, status ?D, stop, total Tv, acumulación hasta 0.5 ml,
no-doble-dosis por hora, rearme al día siguiente, depósito y flag low.
Corre con `python3 apps/esp-32/tests/test_dispenser.py` (CPython).
"""
import sys
import types


class FakeI2C:
    def __init__(self, ack=None):
        self.ack = ack if ack is not None else set()
        self.writes = []
        self._last = {}

    def writeto(self, addr, buf):
        if addr not in self.ack:
            raise OSError("NACK")
        cmd = bytes(buf).decode()
        self.writes.append((addr, cmd))
        self._last[addr] = cmd

    def readfrom(self, addr, n):
        if addr not in self.ack:
            raise OSError("NACK")
        cmd = self._last.get(addr, "")
        if cmd == "i":
            payload = b"TestPMP,1.0"
        elif cmd.startswith("D,") and cmd not in ("D,?",):
            payload = b"*OK"
        elif cmd == "D,?":
            payload = b"?D,0.00,0"
        elif cmd == "X":
            payload = b"*OK"
        elif cmd == "Tv,?":
            payload = b"?Tv,12.50"
        elif cmd == "Sleep":
            payload = b"*OK"
        else:
            payload = b"*ER"
        return (b"\x01" + payload + b"\x00")[:n]


machine = types.ModuleType("machine")
machine.I2C = FakeI2C
sys.modules["machine"] = machine

sys.path.insert(0, "apps/esp-32")

from board import ADDR_EZO_PMP  # noqa: E402
from drivers.dispenser import Doser, EzoPmp  # noqa: E402

assert ADDR_EZO_PMP == 0x67

i2c = FakeI2C(ack={ADDR_EZO_PMP})
pump = EzoPmp(i2c)
assert pump.ping() is True
assert pump.dispense_ml(1.0, sleep=lambda ms: None) is True
assert i2c.writes[-1] == (0x67, "D,1.00"), i2c.writes[-1]
assert pump.pumping() == (0.0, False)
assert pump.stop() is True
assert pump.total_ml() == 12.5
assert pump.sleep_mode() is True
try:
    pump.dispense_ml(0.2)
    raise AssertionError("debió rechazar <0.5 ml")
except ValueError:
    pass
try:
    EzoPmp(FakeI2C(ack=set())).ping()
    raise AssertionError("debió fallar sin bomba")
except OSError:
    pass

# Dosificador: noche acumula (0.2/h) hasta 0.5, día dosifica directo.
sched = tuple([0.2] * 6 + [0.5] * 6 + [1.0] * 6 + [0.5] * 4 + [0.2] * 2)
d = Doser(pump, sched, reservoir_ml=500.0, low_ml=50.0)
assert d.due_ml(0, 1) == 0.0  # 0.2 acumulado, bajo mínimo
assert d.due_ml(1, 1) == 0.0  # 0.4 acumulado
assert abs(d.due_ml(2, 1) - 0.6) < 1e-9  # 0.6 >= 0.5: dosifica
assert d.due_ml(2, 1) == 0.0  # misma hora: no repite
assert d.due_ml(12, 1) == 1.0  # mediodía directo
assert d.dispense(13, 1, sleep=lambda ms: None) == 1.0
assert abs(d.remaining_ml - (500.0 - 1.0)) < 1e-9, d.remaining_ml
assert d.low is False
d.remaining_ml = 0.4
assert d.dispense(14, 2, sleep=lambda ms: None) == 0.0  # ni lo que queda alcanza
d.remaining_ml = 50.0
assert d.low is True
print("dispenser OK: EZO-PMP + tabla horaria + deposito")
