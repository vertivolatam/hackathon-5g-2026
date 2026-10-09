"""Bomba peristáltica Atlas EZO-PMP por I2C (dosis de atrayente etanol+metanol).

La bomba dosifica por VOLUMEN nativo (±1%, mínimo 0.5 ml), así que no
hay que temporizar GPIOs: se le ordena `D,<ml>` y ella cuenta. La dosis
sigue siendo una TABLA HORARIA en config.py (la mezcla se evapora
distinto de día y de noche); como la tabla baja de 0.5 ml/h de noche,
el driver ACUMULA hasta juntar el mínimo dispensable.

Protocolo (EZO_PMP datasheet V3.0): ASCII por I2C en 0x67 (103), bus
compartido GPIO7/8. Tras escribir el comando se esperan 300 ms y se
lee: byte0 = código (1 ok, 2 fallo, 254 aún no, 255 sin datos) +
payload ASCII (`*OK`, `?D,<vol>,<pumping>`...).

Hardware: lógica 3.3V (compatible directo al bus del P4), MOTOR
12–24V → la placa de potencia SHALL proveer riel de 12V (ver
docs de decisiones). Tubo 5 mm O.D., caudal 0.5–105 ml/min.

Requiere hora real (NTP o RTC con batería): sin hora válida NO dosifica.
"""

ADDR_DEFAULT = 0x67
PROCESSING_MS = 300
MIN_ML = 0.5

# Códigos de respuesta EZO (primer byte de la lectura I2C).
CODE_OK = 1
CODE_ERROR = 2
CODE_PENDING = 254
CODE_NO_DATA = 255


class EzoPmp:
    """Driver mínimo EZO-PMP sobre un bus I2C compartido (no lo cierra).

    Args:
        i2c: bus machine.I2C ya inicializado a 400 kHz.
        addr: dirección 7-bit (0x67 default, cambiable con comando I2C).
    """

    def __init__(self, i2c, addr=ADDR_DEFAULT):
        self._i2c = i2c
        self._addr = addr

    def _cmd(self, cmd, delay_ms=PROCESSING_MS, read_len=32, sleep=None):
        """Envía comando ASCII, espera y lee (código, payload).

        Returns:
            tuple[int, str]: (código EZO, payload ASCII sin NULs).
        """
        self._i2c.writeto(self._addr, cmd.encode())
        if sleep is not None and delay_ms > 0:
            sleep(delay_ms)
        try:
            raw = bytes(self._i2c.readfrom(self._addr, read_len))
        except OSError:
            return CODE_NO_DATA, ""
        if not raw:
            return CODE_NO_DATA, ""
        code = raw[0]
        text = raw[1:].split(b"\x00")[0].decode("ascii", "replace").strip()
        return code, text

    def ping(self):
        """True si la bomba responde (comando de información)."""
        code, text = self._cmd("i", sleep=None)
        return code == CODE_OK and bool(text)

    def dispense_ml(self, ml, sleep=None):
        """Dosifica un volumen (ml ≥ 0.5). True si la bomba aceptó."""
        if ml < MIN_ML:
            raise ValueError("EZO-PMP mínimo 0.5 ml (pedido %.2f)" % ml)
        code, _ = self._cmd("D,%.2f" % ml, sleep=sleep)
        return code == CODE_OK

    def pumping(self, sleep=None):
        """(vol_restante, en_marcha) según `D,?`, o (None, None) si falla."""
        code, text = self._cmd("D,?", sleep=sleep)
        if code != CODE_OK or not text.startswith("?D,"):
            return None, None
        try:
            _, vol, run = text.split(",")
            return float(vol), run.strip() == "1"
        except ValueError:
            return None, None

    def stop(self, sleep=None):
        """Detiene la dosificación en curso."""
        code, _ = self._cmd("X", sleep=sleep)
        return code == CODE_OK

    def total_ml(self, sleep=None):
        """Volumen total dispensado desde el último `Tv,clear` (o None)."""
        code, text = self._cmd("Tv,?", sleep=sleep)
        if code != CODE_OK or not text.startswith("?Tv,"):
            return None
        try:
            return float(text.split(",")[1])
        except (ValueError, IndexError):
            return None

    def sleep_mode(self, sleep=None):
        """Duerme la controladora (bajo consumo entre wakes)."""
        code, _ = self._cmd("Sleep", sleep=sleep)
        return code == CODE_OK


class Doser:
    """Política de dosis horaria sobre una EZO-PMP + control de depósito.

    Acumula las horas de <0.5 ml hasta juntar el mínimo de la bomba, y
    lleva el nivel estimado del depósito (el aviso de reposición viaja
    en la telemetría).

    Args:
        pump: EzoPmp ya instanciado.
        schedule_ml: tupla de 24 dosis en ml por hora (config.py).
        reservoir_ml: capacidad del depósito al llenar.
        low_ml: umbral de aviso de nivel bajo.
    """

    def __init__(self, pump, schedule_ml, reservoir_ml=500.0, low_ml=50.0,
                 remaining_ml=None):
        if len(schedule_ml) != 24:
            raise ValueError("schedule de 24 horas, no %d" % len(schedule_ml))
        self._pump = pump
        self._schedule = tuple(schedule_ml)
        self._low = low_ml
        self.remaining_ml = reservoir_ml if remaining_ml is None else remaining_ml
        self._pending = 0.0
        self._last_key = None  # (day, hour) ya contabilizada

    @property
    def low(self):
        """True si el depósito estimado llegó al umbral de reposición."""
        return self.remaining_ml <= self._low

    def due_ml(self, hour, day):
        """Dosis pendiente para (day, hour) con arrastre, o 0.0."""
        if not 0 <= hour <= 23:
            raise ValueError("hora %r fuera de 0..23" % (hour,))
        if self._last_key == (day, hour):
            return 0.0
        self._pending += self._schedule[hour]
        self._last_key = (day, hour)
        if self._pending < MIN_ML:
            return 0.0
        due, self._pending = self._pending, 0.0
        return due

    def dispense(self, hour, day, sleep=None):
        """Dosifica lo pendiente por la bomba. Devuelve ml dosificados."""
        ml = self.due_ml(hour, day)
        if ml <= 0:
            return 0.0
        ml = min(ml, self.remaining_ml)
        if ml < MIN_ML:
            self._pending += ml  # ni lo que queda alcanza: se re-acumula
            return 0.0
        if not self._pump.dispense_ml(ml, sleep=sleep):
            self._pending += ml  # la bomba no aceptó: no se descuenta
            return 0.0
        self.remaining_ml -= ml
        return ml
