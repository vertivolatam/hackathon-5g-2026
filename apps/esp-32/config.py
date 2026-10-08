"""Configuración del nodo trampa (editar antes de flashear).

Toda la parametrización del firmware vive aquí para no tocar lógica.
Nada en este archivo es secreto real de producción: WIFI_PASS y las IP
son de la red de demo del hackathon. Para despliegue en campo, mover
a `secrets.py` (no versionado) o provisioning por el gateway.
"""

# Red WiFi de la demo (la radio va por SDIO vía el módulo C5/C6).
WIFI_SSID = "Hackathon-5G"
WIFI_PASS = "cambiar-esto"

# Broker MQTT (host con `kubectl port-forward svc/mosquitto 1883:1883 -n agrivision`).
MQTT_HOST = "192.168.3.100"
MQTT_PORT = 1883

# Identidad de la trampa en los tópicos `agrivision/*`.
TRAP_ID = "trap-01"

# Periodo de telemetría MQTT en segundos (touch se polea aparte).
INTERVAL_S = 60
# Periodo de polling del GT911 en milisegundos (sin IRQ: sí o sí poleo).
TOUCH_POLL_MS = 100
# Brillo inicial del backlight 0..255 (200 ≈ 80%, diurno legible).
BRIGHTNESS = 200

# Uplink de la trampa: "wifi" (demo/gateway cercano) o "cellular"
# (5G propio por RG255C; requiere placa de potencia con load-switches).
UPLINK = "wifi"
# APN/DNN del operador para el PDP del módem (solo uplink cellular).
# Con NPN privada: un DNN por finca `agrivision.<customer-id>`
# (minúsculas/números/guion, 3GPP TS 23.003; sin device-id: la trampa
# se identifica por SIM + tópico MQTT + TLS).
# En campo viene de secrets.py/provisioning, nunca de este archivo.
MODEM_APN = "internet"
# Ciclo de energía con 5G propio (ver drivers/power.py para el modelo).
WAKE_PERIOD_S = 900  # wake cada 15 min (+ desfase por trampa)
WAKE_ACTIVE_S = 45   # ventana módem+captura+publish
