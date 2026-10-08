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

# Atrayente etanol+metanol por EZO-PMP (ml por hora 0..23).
# Más dosis 12-17h (evaporación + vuelo de broca), mínima de noche.
# Punto de partida a calibrar en campo. La bomba exige >=0.5 ml por
# orden: el driver acumula horas chicas (ver drivers/dispenser.py).
DISPENSE_ML_PER_HOUR = (
    0.2, 0.2, 0.2, 0.2, 0.2, 0.2,  # 00-05 noche
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # 06-11 mañana
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 12-17 tarde
    0.5, 0.5, 0.5, 0.5,            # 18-21 atardecer
    0.2, 0.2,                      # 22-23 noche
)
# Luz ambiental BH1750: bajo este umbral (lux) es de noche y se
# enciende el iluminador para seguir capturando broca.
LUX_NIGHT_THRESHOLD = 10.0
# Iluminador nocturno (LED blanco/IR por MOSFET en NIGHT_LIGHT_GPIO).
NIGHT_LIGHT_ENABLED = True
# Depósito en ml al llenar + umbral de aviso (va en la telemetría).
RESERVOIR_ML = 500.0
RESERVOIR_LOW_ML = 50.0
# False = solo reporta dosis sin accionar (banco/PoC sin bomba).
DISPENSE_ENABLED = True
