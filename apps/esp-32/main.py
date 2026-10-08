"""Bring-up ESP32-P4-NANO en MicroPython (port de src/main.rs).

Replica el flujo del firmware Rust original, en el mismo orden:
I2C0 a 400 kHz en GPIO7/8 -> backlight 80% -> chip_id del ES8311 ->
probe + polling del GT911 -> probe SCCB de cámara. Luego entra al loop:
poleo táctil cada TOUCH_POLL_MS y telemetría MQTT `agrivision/telemetry`
cada INTERVAL_S.

Requiere placa con MicroPython + network + umqtt.simple. En ESP32-P4-NANO
el soporte MicroPython es experimental: si I2C/WiFi falla, ver README
(camino ESP-IDF o gateway como puente serial->MQTT).
"""
import json
import time

import config
from board import I2C_FREQ_HZ, I2C_SCL_GPIO, I2C_SDA_GPIO
from board import ADDR_EZO_PMP
from drivers import camera, display
from drivers.backlight import Backlight
from drivers.dispenser import Doser, EzoPmp
from drivers.es8311 import CHIP_ID_EXPECTED, Es8311
from drivers.gt911 import Gt911
from drivers.modem import Modem
from drivers.net import rmii_summary
from drivers.power import PowerDomain, wake_offset_s

_doser = None  # Doser de atrayente (None hasta crearla en main)
_last_rssi = None  # dBm del módem tras registro (None = sin uplink cellular)


def bring_up(i2c):
    """Ejecuta el bring-up de periféricos en orden y reporta por serie.

    Cada paso es tolerante a fallo: si un periférico no responde se
    imprime el NACK accionable y se sigue con el siguiente, igual que
    el firmware Rust original. Nada de lo impreso aquí detiene el boot.

    Args:
        i2c: bus I2C ya inicializado (machine.I2C a 400 kHz).

    Returns:
        Gt911 | None: instancia del touch si respondió al probe, o None
            si no hay panel táctil (el loop principal lo tolera).
    """
    print("esp32-p4-nano-fw boot: P4NRW32 + I2C SDA=GPIO7 SCL=GPIO8")
    found = sorted(i2c.scan())
    print("i2c scan:", [hex(a) for a in found])

    # 1) Backlight al 80%: si falla, el panel queda oscuro pero el resto sigue.
    try:
        Backlight(i2c).set_brightness(config.BRIGHTNESS)
        print("backlight ok (0x45:0x96=%d)" % config.BRIGHTNESS)
    except OSError:
        print("backlight NACK: revisa flat MIPI-DSI / 5V")

    # 2) Sanity del codec de audio: chip_id esperado 0x83.
    try:
        cid = Es8311(i2c).chip_id()
        print("es8311 chip_id=0x%02x%s" % (cid, "" if cid == CHIP_ID_EXPECTED else " (inesperado)"))
    except OSError:
        print("es8311 NACK en 0x18")

    # 3) Touch: probe 0x5D/0x14; sin ACK no hay polling (cable suelto?).
    try:
        gt = Gt911.probe(i2c)
        print("gt911 ok addr=0x%02x (polling)" % gt.address)
    except OSError:
        print("gt911 NACK 0x5D/0x14: display sin touch o cable suelto")
        gt = None

    # 4) Cámara: solo presencia SCCB (sin driver CSI en 2026).
    hit = camera.probe_sccb(i2c)
    if hit is not None:
        print("camera SCCB ACK 0x%02x" % hit)
    else:
        print("camera sin ACK (normal sin modulo CSI)")

    # 5) Contratos impresos (red por RMII y display nativo van por ESP-IDF).
    print("eth:", rmii_summary())
    print("display:", display.note())
    # 6) Energía con 5G propio: reporta el desfase de wake (evita que las
    # trampas registren a la vez) sin encender nada en el bring-up.
    print("wake offset=%ds/%ds uplink=%s"
          % (wake_offset_s(config.TRAP_ID, config.WAKE_PERIOD_S),
             config.WAKE_PERIOD_S, config.UPLINK))
    return gt


def cellular_uplink(Pin, UART):
    """Uplink 5G propio: enciende módem, registra y levanta PDP.

    Best-effort como el MQTT: si el módem no registra, se apaga y se
    devuelve None (el nodo sigue en local). La MIPI de la cámara no se
    toca: su riel se gestiona en la ventana de captura, no aquí.

    Args:
        Pin: machine.Pin (inyectable en tests).
        UART: machine.UART (inyectable en tests).

    Returns:
        Modem | None: módem registrado con PDP activo, o None.
    """
    import time

    from board import MODEM_PWR_GPIO, MODEM_RESET_GPIO
    from board import MODEM_RX_GPIO, MODEM_TX_GPIO

    modem_pwr = PowerDomain(Pin(MODEM_PWR_GPIO), "modem")
    rst = Pin(MODEM_RESET_GPIO)
    try:
        rst.on()  # RESET_N idle en alto
    except AttributeError:
        rst.value(1)
    modem_pwr.on(sleep=time.sleep_ms)
    uart = UART(1, baudrate=115200, tx=MODEM_TX_GPIO, rx=MODEM_RX_GPIO)
    mdm = Modem(uart, config.MODEM_APN)
    if not mdm.alive():
        print("modem sin respuesta AT (revisa 3.7V/antenas)")
        modem_pwr.off()
        return None
    if not mdm.wait_registered(sleep=time.sleep_ms):
        print("modem sin registro (SIM/cobertura/APN)")
        modem_pwr.off()
        return None
    rssi = mdm.signal_dbm()
    print("modem registrado rssi=%s dBm" % (rssi,))
    global _last_rssi
    _last_rssi = rssi  # la telemetría lo publica (ver read_sensors)
    if not mdm.pdp_up():
        print("modem PDP caído (revisa APN)")
        modem_pwr.off()
        return None
    print("cellular PDP ok")
    return mdm


def mqtt_client():
    """Conecta al broker MQTT del backend.

    Returns:
        umqtt.simple.MQTTClient: cliente ya conectado, listo para publish.

    Raises:
        OSError: si el broker no responde (red caída, port-forward abajo).
        Exception: cualquier otro fallo de la capa umqtt.
    """
    from umqtt.simple import MQTTClient

    mq = MQTTClient(config.TRAP_ID, config.MQTT_HOST, port=config.MQTT_PORT)
    mq.connect()
    print("mqtt ok:", config.MQTT_HOST)
    return mq


def read_sensors():
    """Lee los sensores de la trampa (placeholder con valores de demo).

    Returns:
        dict: telemetría con trap_id, temperatura, humedad, conteo y,
            si hay dosificador, nivel estimado de cebo (ml + flag low).
            Sustituir por DHT22/ADC/contador real de la trampa.
    """
    data = {"trap_id": config.TRAP_ID, "temp_c": 24.5, "hum_pct": 78.0, "count": 0}
    if _doser is not None:
        data["cebo_ml"] = round(_doser.remaining_ml, 1)
        data["cebo_low"] = bool(_doser.low)
    if _last_rssi is not None:
        data["rssi_dbm"] = _last_rssi
    return data


def main():
    """Punto de entrada: bring-up, MQTT best-effort y loop eterno.

    El MQTT es best-effort: si el broker no responde al arrancar, el nodo
    sigue poleando el touch (modo offline) en vez de reiniciarse. El loop
    mezcla dos periodos: touch cada TOUCH_POLL_MS y telemetría cada
    INTERVAL_S, sin threads (MicroPython cooperativo simple).
    """
    from machine import I2C, Pin

    global _doser

    i2c = I2C(0, sda=Pin(I2C_SDA_GPIO), scl=Pin(I2C_SCL_GPIO), freq=I2C_FREQ_HZ)
    gt = bring_up(i2c)

    try:
        _doser = Doser(
            EzoPmp(i2c, ADDR_EZO_PMP),
            config.DISPENSE_ML_PER_HOUR,
            reservoir_ml=config.RESERVOIR_ML,
            low_ml=config.RESERVOIR_LOW_ML,
        )
        print("dosificador EZO-PMP ok (cebo %.0f ml)" % _doser.remaining_ml)
    except Exception as e:
        print("dosificador offline:", e)
        _doser = None

    if config.UPLINK == "cellular":
        from machine import UART

        cellular_uplink(Pin, UART)  # best-effort; el loop sigue en local

    try:
        mq = mqtt_client()
    except Exception as e:
        print("mqtt offline:", e)
        mq = None

    last_pub = 0
    while True:
        # Touch: polling rápido, solo loguea cuando hay dedo.
        if gt is not None:
            try:
                pt = gt.read_first_point()
                if pt is not None:
                    print("touch x=%d y=%d s=%d" % (pt.x, pt.y, pt.size))
            except OSError:
                print("gt911 read err")
        # Telemetría: publish lento al backend para la landing.
        now = time.time()
        if mq is not None and now - last_pub >= config.INTERVAL_S:
            mq.publish("agrivision/telemetry", json.dumps(read_sensors()).encode())
            last_pub = now
        # Dosificación: una vez por hora de reloj (RTC/NTP). Sin año
        # válido (>=2026) no hay hora real y NO se dosifica (fail-safe).
        if _doser is not None and config.DISPENSE_ENABLED:
            try:
                t = time.localtime()
                if t[0] >= 2026:
                    ml = _doser.dispense(t[3], t[7], sleep=time.sleep_ms)
                    if ml > 0:
                        print("cebo %.1f ml (quedan %.0f)" % (ml, _doser.remaining_ml))
            except OSError:
                print("bomba EZO sin ACK en 0x67")
        time.sleep_ms(config.TOUCH_POLL_MS)


if __name__ == "__main__":
    main()
