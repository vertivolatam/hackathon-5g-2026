"""Táctil capacitivo GT911 en modo polling (port de touch.rs).

RST/INT no están ruteados en la NANO, así que no hay reset por GPIO ni
interrupción: el firmware polea el registro de estado. Se prueban las
dos direcciones documentadas por Waveshare (0x5D primero, luego 0x14)
porque el panel montado puede usar cualquiera.
"""
from board import ADDR_GT911_A, ADDR_GT911_B

# Mapa de registros GT911 (direcciones de 16 bits, big-endian en el bus).
REG_STATUS = 0x814E  # bit7 = buffer ready, bits[3:0] = nº de toques
REG_TOUCH1_X = 0x8150  # bloque de 6B: Xle16, Yle16, size, reservado
FLAG_BUFFER_READY = 0x80


class TouchPoint:
    """Un dedo detectado en el panel.

    Attributes:
        x: coordenada horizontal en píxeles (little-endian del sensor).
        y: coordenada vertical en píxeles.
        size: área/presión reportada por el sensor.
    """

    def __init__(self, x, y, size):
        """Guarda las coordenadas y el tamaño ya decodificados."""
        self.x, self.y, self.size = x, y, size

    def __repr__(self):
        """Representación compacta para el log por serie."""
        return "TouchPoint(x=%d, y=%d, size=%d)" % (self.x, self.y, self.size)


class Gt911:
    """Driver polling del GT911.

    Args:
        i2c: bus I2C ya inicializado (machine.I2C). Compartido.
        addr: dirección 7-bit que respondió al probe (0x5D o 0x14).
    """

    def __init__(self, i2c, addr):
        """Guarda bus y dirección detectada (sin tomar ownership del bus)."""
        self.i2c = i2c
        self.addr = addr

    @classmethod
    def probe(cls, i2c):
        """Detecta el GT911 probando 0x5D y luego 0x14.

        Lee el registro de estado en cada dirección y se queda con la
        primera que hace ACK.

        Args:
            i2c: bus I2C ya inicializado.

        Returns:
            Gt911: instancia ligada a la dirección que respondió.

        Raises:
            OSError: si ninguna dirección responde. Típico: flat cable
                del display suelto o panel sin touch.
        """
        last = None
        for addr in (ADDR_GT911_A, ADDR_GT911_B):
            try:
                i2c.readfrom_mem(addr, REG_STATUS, 1)
                return cls(i2c, addr)
            except OSError as e:
                last = e
        raise last

    @property
    def address(self):
        """Dirección 7-bit del chip detectado (0x5D o 0x14)."""
        return self.addr

    def read_first_point(self):
        """Lee el primer punto táctil, si hay un dedo presente.

        Requiere buffer-ready (bit7) y al menos 1 toque (bits[3:0]);
        en otro caso devuelve None sin tocar el bus de más. Tras leer,
        limpia el flag escribiendo 0 para que el sensor reporte el
        siguiente evento.

        Returns:
            TouchPoint | None: el punto, o None si no hay dedo.

        Raises:
            OSError: si el sensor deja de responder a mitad del ciclo.
        """
        status = self.i2c.readfrom_mem(self.addr, REG_STATUS, 1)[0]
        if not (status & FLAG_BUFFER_READY) or not (status & 0x0F):
            return None
        raw = self.i2c.readfrom_mem(self.addr, REG_TOUCH1_X, 6)
        x = raw[0] | (raw[1] << 8)
        y = raw[2] | (raw[3] << 8)
        pt = TouchPoint(x, y, raw[4])
        # Limpia buffer-ready para el siguiente evento.
        self.i2c.writeto_mem(self.addr, REG_STATUS, bytes([0x00]))
        return pt
