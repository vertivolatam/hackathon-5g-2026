"""Agente Python del gateway (Raspberry Pi): puente entre trampa, MQTT y backend.

Ciclo:
  1. Lee sensores / captura foto (inyectable: cámara local, ESP32 por serial, demo).
  2. Publica telemetría en MQTT `agrivision/telemetry`.
  3. Envía la foto al backend `POST /api/detect` (el backend corre el
     modelo RF-DETR en Roboflow y republica en `agrivision/detections`).
  4. Reenvía detecciones relevantes (broca/roya sobre umbral) a `agrivision/alertas`.

Config por entorno: MQTT_HOST, MQTT_PORT, BACKEND_URL, TRAP_ID, INTERVAL_S.
"""

import base64
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001").rstrip("/")
TRAP_ID = os.getenv("TRAP_ID", "trap-01")
INTERVAL_S = int(os.getenv("INTERVAL_S", "60"))
IMAGE_PATH = os.getenv("IMAGE_PATH", "")  # foto de prueba / cámara vía script externo
ALERT_CLASSES = set(os.getenv("ALERT_CLASSES", "broca").split(","))
ALERT_MIN_CONF = float(os.getenv("ALERT_MIN_CONF", "0.5"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_sensors() -> dict:
    """Placeholder: aquí va DHT22/DS18B20/contador de trampa por GPIO/serial."""
    return {"trap_id": TRAP_ID, "temp_c": 24.5, "hum_pct": 78.0, "count": 0}


def capture_image_b64() -> str | None:
    if not IMAGE_PATH or not os.path.exists(IMAGE_PATH):
        return None
    with open(IMAGE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def backend_detect(image_b64: str) -> dict:
    body = json.dumps({"trap_id": TRAP_ID, "image_base64": image_b64}).encode()
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/detect",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    print(f"[{TRAP_ID}] gateway agent -> mqtt={MQTT_HOST}:{MQTT_PORT} backend={BACKEND_URL}")
    while True:
        tel = {**read_sensors(), "ts": now_iso()}
        client.publish("agrivision/telemetry", json.dumps(tel))
        print("telemetry:", tel)

        img = capture_image_b64()
        if img:
            try:
                res = backend_detect(img)
                print(f"detections: {len(res.get('detections', []))}")
                for d in res.get("detections", []):
                    if d.get("class") in ALERT_CLASSES and (d.get("confidence") or 0) >= ALERT_MIN_CONF:
                        client.publish("agrivision/alertas", json.dumps({**d, "trap_id": TRAP_ID, "ts": now_iso()}))
                        print("ALERTA:", d)
            except Exception as e:
                print("detect error:", e)
        else:
            print("sin IMAGE_PATH: solo telemetría (define IMAGE_PATH con una foto de campo)")
        time.sleep(INTERVAL_S)


if __name__ == "__main__":
    main()
