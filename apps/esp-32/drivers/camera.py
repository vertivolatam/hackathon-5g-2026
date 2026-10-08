"""Cámara MIPI-CSI + bus SCCB (port de camera.rs).

Hardware real: OV5647 5MP (KIT-C del ESP32-P4-NANO, PoC inmediato) o
onsemi AR1335 13MP vía adaptador FPC (el kit EVK trae conector de 70
pines para SOMs NXP, no directo al P4; el CSI del P4 es de 2 lanes).

Estado 2026: ni MicroPython ni esp-hal traen driver CSI/ISP/V4L2, así que
no hay captura desde este firmware. Este módulo deja el contrato SCCB
(I2C en GPIO7/8, XCLK/RESET no conectados, sensor en free-run) y el
probe de presencia. El pipeline real de visión es ESP-IDF `esp_video`
(CSI receiver + ISP + JPEG/H264).
"""

# Candidatos típicos según el módulo montado: OV5647 0x36, SC2336 0x30,
# AR1335 (verificar contra el datasheet del módulo/adaptador).
SCCB_CANDIDATES = (0x36, 0x30, 0x3C)


def probe_sccb(i2c, candidates=SCCB_CANDIDATES):
    """Busca el sensor de cámara probando direcciones SCCB.

    Escribe 1 byte en cada candidata y se queda con la primera que hace
    ACK (el contenido del byte es irrelevante: solo importa el ACK).

    Args:
        i2c: bus I2C ya inicializado (machine.I2C). Compartido.
        candidates: direcciones 7-bit a probar, en orden de prioridad.

    Returns:
        int | None: dirección del sensor, o None si no hay módulo CSI
            (caso normal en bring-up sin cámara montada).
    """
    for addr in candidates:
        try:
            i2c.writeto(addr, b"\x00")
            return addr
        except OSError:
            continue
    return None
