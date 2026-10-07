"""boot.py: arranque MicroPython (corre antes que main.py).

Solo levanta WiFi con un reintento corto y tolerante a fallo: si no hay
red, imprime el error y sigue, porque el bring-up de periféricos
(backlight/touch/audio) no depende de la red y main.py reintenta MQTT
por su cuenta. Nada de hardware se inicializa aquí.
"""
import config
from drivers.net import wifi_connect

try:
    print("boot: wifi", config.WIFI_SSID)
    print("boot: net", wifi_connect(config.WIFI_SSID, config.WIFI_PASS))
except Exception as e:
    # Offline-first: el nodo sigue útil (sensores + display) sin red.
    print("boot: sin wifi, sigo offline:", e)
