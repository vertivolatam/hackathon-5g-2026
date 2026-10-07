"""Codec de audio ES8311 por I2C (port de audio.rs).

Solo control I2C (reset, relojes, power del DAC, chip-id). El stream de
audio I2S (GPIO9..13) lo maneja machine.I2S por separado. Tras un
init_playback() exitoso, el caller debe subir PA_CTRL (GPIO53) para
habilitar el amplificador NS4150B hacia el parlante 8Ω 2W.
"""
from board import ADDR_ES8311

# Registros del ES8311 usados en la secuencia mínima audible.
REG_RESET = 0x00  # 0x80 = reset, luego 0x00 = run
REG_CLK_MANAGER = 0x01  # 0x3F = MCLK presente (GPIO13), BCLK 48 kHz típico
REG_DAC_POWER = 0x12  # 0x00 = DAC encendido
REG_DAC_CTRL = 0x10  # 0x1C = PGA en valor típico
REG_CHIP_ID = 0xFD  # solo lectura; valor esperado CHIP_ID_EXPECTED
CHIP_ID_EXPECTED = 0x83


class Es8311:
    """Driver mínimo del codec ES8311.

    Args:
        i2c: bus I2C ya inicializado (machine.I2C). Compartido; esta
            clase nunca lo cierra ni lo reconfigura.
    """

    def __init__(self, i2c):
        """Guarda la referencia al bus compartido (sin tomar ownership)."""
        self.i2c = i2c

    def init_playback(self):
        """Aplica la secuencia mínima para playback audible.

        Orden: reset (0x80 -> 0x00), clock manager, DAC power, DAC ctrl.
        No configura I2S ni sample-rate fino: ver datasheet para la
        tabla completa de registros.

        Raises:
            OSError: si el codec no responde (NACK en 0x18). Revisar
                pull-ups del bus y alimentación del codec.
        """
        self.i2c.writeto(ADDR_ES8311, bytes([REG_RESET, 0x80]))
        self.i2c.writeto(ADDR_ES8311, bytes([REG_RESET, 0x00]))
        self.i2c.writeto(ADDR_ES8311, bytes([REG_CLK_MANAGER, 0x3F]))
        self.i2c.writeto(ADDR_ES8311, bytes([REG_DAC_POWER, 0x00]))
        self.i2c.writeto(ADDR_ES8311, bytes([REG_DAC_CTRL, 0x1C]))

    def chip_id(self):
        """Lee el registro CHIP_ID como sanity-check del bus.

        Returns:
            int: byte leído del registro 0xFD (esperado 0x83).

        Raises:
            OSError: si el codec no responde (NACK en 0x18).
        """
        return self.i2c.readfrom_mem(ADDR_ES8311, REG_CHIP_ID, 1)[0]
