"""Módem 5G RedCap por UART-AT (Quectel RG255C, 3GPP R17).

El RG255C expone datos por USB 2.0 (ECM/MBIM, camino ESP-IDF con USB
host) y control total por UART-AT. Este driver implementa el plano de
control mínimo que funciona igual en MicroPython y ESP-IDF:

  registro (C5GREG/CEREG) -> calidad (CSQ) -> PDP (CGDCONT/CGACT).

El plano de datos en MicroPython es AT+QMT* (MQTT nativo del módem,
depende de la versión de firmware) o PPP por UART; en producción
ESP-IDF el P4 levanta ECM por USB-OTG como interfaz de red. Ver la
ficha en docs-site/docs/reference/hardware/rg255c-redcap.md.

Nota de escala: con 5G por trampa, el attach es lo más caro en tiempo
y energía (~decenas de segundos). El wake se desfasa por trampa
(drivers/power.py:wake_offset_s) y el módem se apaga fuera de ventana.
"""

# (U)SIM y modos de registro aceptados como "en servicio".
REG_OK = ("1", "5")  # 1=home, 5=roaming

# Módem TOP #1 de compatibilidad (ver requisitos-criticos.md). El driver
# habla AT 3GPP estándar (funciona en RedCap de cualquier vendor), pero
# verifica el modelo por ATI y avisa si no es el esperado.
MODEM_TOP1 = "RG255C"


class Modem:
    """Cliente AT mínimo. `uart` implementa write(bytes)+readline().

    Args:
        uart: puerto serie ya configurado (115200 8N1 típico del RG255C).
        apn: APN del operador (entra por config, nunca en git).
    """

    def __init__(self, uart, apn):
        self._uart = uart
        self._apn = apn
        self._buf = b""

    def _cmd(self, at, timeout_ms=2000, read=None):
        """Envía un comando y recoge líneas hasta OK/ERROR o timeout."""
        self._uart.write((at + "\r").encode())
        lines = []
        waited = 0
        step = 100
        while True:
            chunk = read(step) if read is not None else None
            if chunk is None:
                chunk = self._uart.readline()
            if chunk:
                waited = 0
                text = chunk.decode("utf-8", "replace").strip()
                if text:
                    lines.append(text)
                if text in ("OK", "ERROR"):
                    break
            else:
                waited += step
                if waited >= timeout_ms:
                    break
        return lines

    def alive(self):
        """True si el módem responde AT (eco + OK)."""
        return "OK" in self._cmd("ATE1")

    def identify(self):
        """Texto de ATI (fabricante + modelo + revisión), o None si no responde."""
        lines = [ln for ln in self._cmd("ATI")
                 if ln and ln not in ("OK", "ERROR") and not ln.startswith("AT")]
        return " ".join(lines) if lines else None

    def check_model(self, expected=MODEM_TOP1):
        """True si el modelo coincide con el TOP #1 (avisa si es otro)."""
        model = self.identify()
        if model is None:
            return False
        return expected in model

    def registration(self):
        """Estado de registro NR/LTE: (tecnología, stat) o (None, None).

        Prueba C5GREG (SA RedCap) y cae a CEREG (LTE). stat "1"/"5"
        significa en servicio.
        """
        for cmd in ("AT+C5GREG?", "AT+CEREG?"):
            for line in self._cmd(cmd):
                if line.startswith("+C5GREG:") or line.startswith("+CEREG:"):
                    parts = line.split(",")
                    stat = parts[-1].strip().strip('"')
                    tech = "NR" if "C5G" in line else "LTE"
                    return tech, stat
        return None, None

    def wait_registered(self, poll_ms=5000, tries=12, sleep=None):
        """Espera registro en red. True si quedó en servicio."""
        for _ in range(max(tries, 1)):
            tech, stat = self.registration()
            if stat in REG_OK:
                return True
            if sleep is not None:
                sleep(poll_ms)
        return False

    def signal_dbm(self):
        """RSSI aproximado en dBm vía CSQ, o None si inválido (99,99)."""
        for line in self._cmd("AT+CSQ"):
            if line.startswith("+CSQ:"):
                try:
                    rssi = int(line.split(":")[1].split(",")[0])
                except ValueError:
                    return None
                if rssi in (99, 199):
                    return None
                return -113 + 2 * rssi
        return None

    def pdp_up(self):
        """Levanta el contexto de datos con el APN (CGDCONT + CGACT)."""
        self._cmd('AT+CGDCONT=1,"IPV4V6","%s"' % self._apn)
        lines = self._cmd("AT+CGACT=1,1", timeout_ms=30000)
        return "OK" in lines
