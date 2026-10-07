"""Bring-up ESP32-P4-NANO en MicroPython (port de src/main.rs).

Replica el flujo del firmware Rust original, en el mismo orden:
I2C0 a 400 kHz en GPIO7/8 -> backlight 80% -> chip_id del ES8311 ->
probe + polling del GT911 -> probe SCCB de cámara. Luego entra al loop:
poleo táctil cada TOUCH_POLL_MS y telemetría MQTT `biotrap/telemetry`
cada INTERVAL_S.

Requiere placa con MicroPython + network + umqtt.simple. En ESP32-P4-NANO
el soporte MicroPython es experimental: si I2C/WiFi falla, ver README
(camino ESP-IDF o gateway como puente serial->MQTT).
"""
import json
import time

import config
from board import I2C_FREQ_HZ, I2C_SCL_GPIO, I2C_SDA_GPIO
from drivers import camera, display
from drivers.backlight import Backlight
from drivers.es8311 import CHIP_ID_EXPECTED, Es8311
from drivers.gt911 import Gt911
from drivers.net import rmii_summary


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
    return gt


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
        dict: telemetría con trap_id, temperatura, humedad y conteo.
            Sustituir por DHT22/ADC/contador real de la trampa.
    """
    return {"trap_id": config.TRAP_ID, "temp_c": 24.5, "hum_pct": 78.0, "count": 0}


def main():
    """Punto de entrada: bring-up, MQTT best-effort y loop eterno.

    El MQTT es best-effort: si el broker no responde al arrancar, el nodo
    sigue poleando el touch (modo offline) en vez de reiniciarse. El loop
    mezcla dos periodos: touch cada TOUCH_POLL_MS y telemetría cada
    INTERVAL_S, sin threads (MicroPython cooperativo simple).
    """
    from machine import I2C, Pin

    i2c = I2C(0, sda=Pin(I2C_SDA_GPIO), scl=Pin(I2C_SCL_GPIO), freq=I2C_FREQ_HZ)
    gt = bring_up(i2c)

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
            mq.publish("biotrap/telemetry", json.dumps(read_sensors()).encode())
            last_pub = now
        time.sleep_ms(config.TOUCH_POLL_MS)


if __name__ == "__main__":
    main()
