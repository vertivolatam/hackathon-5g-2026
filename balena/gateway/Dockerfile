FROM balenalib/raspberrypi4-64-debian:bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl xz-utils python3 python3-pip \
 && rm -rf /var/lib/apt/lists
WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt
COPY agent.py .
# Config por entorno (ver ../docker-compose.yml): MQTT_HOST, MQTT_PORT,
# BACKEND_URL, TRAP_ID, INTERVAL_S, ALERT_CLASSES, ALERT_MIN_CONF.
# El uplink 5G lo da el HAT RM520N-GL por USB (MBIM); el agent no cambia.
CMD ["python3", "agent.py"]
