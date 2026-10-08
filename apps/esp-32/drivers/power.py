"""Gestión de energía de la trampa con 5G propio (port de power.rs inexistente: diseño nuevo).

Cada trampa lleva su módem 5G RedCap (Quectel RG255C: sleep ~3.6 mA,
idle ~29 mA @3.3V, picos TX de ~2W) + cámara AR1335 (≤723 mW activa).
Sin gestión, el módem y la cámara agotan cualquier batería solar en
días. La política es duty-cycle con load-switches por GPIO:

  SLEEP (casi todo el día): P4 en deep-sleep, módem OFF (0 mA),
      cámara OFF (0 mW, ni siquiera su standby HW de 26 mW).
  WAKE (decenas de segundos): rieles de cámara ON → captura →
      módem ON → espera registro → publica → todo OFF.

Los GPIO de los load-switches dependen del esquemático de la placa de
potencia (ver board.py: sección POWER, ajustar a la rev construida).
La interfaz MIPI de la cámara NO cambia: solo se gatea su alimentación;
CSI-2 2-lane, I2C SCCB y timings quedan intactos.

Presupuesto (estimaciones de datasheet, validar en banco):
  RG255C mini-PCIe: sleep 3.6 mA / idle 29 mA @3.3V; TX ~2W pico.
  AR1335: 723 mW activa / 26 mW standby HW (por eso se apaga del todo).
  P4 activo (CPU+PSRAM, radio WiFi apagada): ~0.75W (TBD medición).
"""

# Potencias de diseño en vatios (datasheets RG255C + AR1335 + estimado P4).
P_MODEM_IDLE_W = 0.10    # 29 mA @3.3V
P_MODEM_TX_AVG_W = 1.0   # promedio durante la ventana (picos ~2W)
P_CAM_ACTIVE_W = 0.723
P_SLEEP_W = 0.05         # P4 deep-sleep + fugas de los switches

# Ventana típica de wake: attach+registro 5G (lo dominante) + captura + publish.
WAKE_PERIOD_S = 900      # cada 15 min
WAKE_ACTIVE_S = 45
CAM_ON_S = 5             # rieles de cámara solo para capturar


def wake_offset_s(trap_id, period_s=WAKE_PERIOD_S, slots=60):
    """Desfase de wake para no registrar 1000 trampas a la vez.

    Reparte los wakes en `slots` ranuras deterministas por trap_id, de
    modo que los attaches 5G no colapsen la celda rural al mismo segundo.

    Args:
        trap_id: identidad de la trampa (str, ej. "trap-0042").
        period_s: periodo del ciclo de wake.
        slots: ranuras por periodo.

    Returns:
        int: segundos a esperar tras el múltiplo del periodo.
    """
    h = 0
    for ch in str(trap_id):
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return (h % slots) * (period_s // slots)


def daily_energy_wh(period_s=WAKE_PERIOD_S, active_s=WAKE_ACTIVE_S,
                    cam_s=CAM_ON_S):
    """Energía diaria estimada en Wh (dimensiona panel + batería).

    Returns:
        float: Wh/día. Ej. 900/45/5 -> ~4.3 Wh/día (ver docstring).
    """
    p_active = P_MODEM_TX_AVG_W + 0.75  # módem TX + P4 activo
    e_cycle = active_s * p_active + cam_s * P_CAM_ACTIVE_W \
        + (period_s - active_s) * P_SLEEP_W
    return e_cycle * (86400.0 / period_s) / 3600.0


class PowerDomain:
    """Un riel conmutado por load-switch (módem o cámara).

    Args:
        pin: objeto pin con métodos .on()/.off() (machine.Pin) o
            .value(1)/.value(0). Activo alto por defecto.
        name: nombre para el log.
        settle_ms: espera tras encender (sleep inyectable en tests).
    """

    def __init__(self, pin, name, settle_ms=0):
        self._pin = pin
        self._name = name
        self._settle_ms = settle_ms
        self.is_on = False

    def _set(self, on):
        try:
            self._pin.on() if on else self._pin.off()
        except AttributeError:
            self._pin.value(1 if on else 0)
        self.is_on = bool(on)

    def on(self, sleep=None):
        """Enciende el riel y espera estabilización."""
        self._set(True)
        if self._settle_ms and sleep is not None:
            sleep(self._settle_ms)
        return True

    def off(self):
        """Apaga el riel (corriente cero, ni standby)."""
        self._set(False)
        return True
