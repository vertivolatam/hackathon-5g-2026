"""AgriVision backend: ingest MQTT (agrivision/#) y expone HTTP para la landing."""
import json
import os
import threading
import time
from collections import deque
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from vision import configured as rf_configured
from vision import detect_b64 as rf_detect

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "agrivision/#")
MAX_ITEMS = 200

store: deque = deque(maxlen=MAX_ITEMS)
detections: deque = deque(maxlen=MAX_ITEMS)
mqtt_state = {"connected": False, "last_error": None}
_mqtt_client = None

app = FastAPI(title="AgriVision API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TelemetryIn(BaseModel):
    topic: str = "agrivision/demo"
    payload: dict = {}


class DetectIn(BaseModel):
    trap_id: str = "trap-01"
    image_base64: str = ""  # JPEG/PNG codificado en base64
    publish_mqtt: bool = True


def _record(topic: str, payload, raw: str | None = None):
    item = {
        "topic": topic,
        "payload": payload,
        "raw": raw,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    store.append(item)
    return item


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        mqtt_state["connected"] = True
        mqtt_state["last_error"] = None
        client.subscribe(MQTT_TOPIC)
    else:
        mqtt_state["connected"] = False
        mqtt_state["last_error"] = f"rc={rc}"


def _on_disconnect(client, userdata, rc):
    mqtt_state["connected"] = False


def _on_message(client, userdata, msg):
    # Ignora el tópico propio: el backend publica resultados en
    # agrivision/detections y el subscribe es agrivision/#. Sin este filtro,
    # cada /api/detect duplicaría su resultado en el feed de telemetría.
    if msg.topic == "agrivision/detections":
        return
    raw = msg.payload.decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        payload = {"value": raw}
    _record(msg.topic, payload, raw=raw)


def _mqtt_loop():
    global _mqtt_client
    client = mqtt.Client()
    _mqtt_client = client
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message = _on_message
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            client.loop_forever()
        except Exception as e:  # broker aún no listo
            mqtt_state["connected"] = False
            mqtt_state["last_error"] = str(e)
            time.sleep(5)


@app.on_event("startup")
def _startup():
    t = threading.Thread(target=_mqtt_loop, daemon=True)
    t.start()


@app.get("/health")
def health():
    return {
        "status": "ok",
        **mqtt_state,
        "buffered": len(store),
        "detections": len(detections),
        "roboflow": {"configured": rf_configured()},
    }


@app.get("/api/telemetry")
def list_telemetry(limit: int = 20):
    items = list(store)[-limit:]
    return {"count": len(items), "items": list(reversed(items))}


@app.get("/api/telemetry/latest")
def latest():
    if not store:
        raise HTTPException(status_code=404, detail="sin datos")
    return store[-1]


@app.post("/api/telemetry", status_code=201)
def ingest(body: TelemetryIn):
    return _record(body.topic, body.payload)


@app.post("/api/detect", status_code=201)
def detect(body: DetectIn):
    """Recibe foto en base64, la envía al modelo RF-DETR hosteado en
    Roboflow (clase prioritaria: broca) y publica el resultado en
    MQTT `agrivision/detections`."""
    if not body.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 vacío")
    if not rf_configured():
        raise HTTPException(
            status_code=503,
            detail="Roboflow no configurado (ROBOFLOW_API_KEY / ROBOFLOW_MODEL_ID)",
        )
    try:
        rf = rf_detect(body.image_base64)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    preds = [
        {
            "class": p.get("class"),
            "confidence": p.get("confidence"),
            "bbox": {k: p.get(k) for k in ("x", "y", "width", "height")},
        }
        for p in rf.get("predictions", [])
    ]
    result = {
        "trap_id": body.trap_id,
        "model": rf.get("model_id", ""),
        "detections": preds,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    detections.append(result)
    if body.publish_mqtt and _mqtt_client and mqtt_state["connected"]:
        _mqtt_client.publish("agrivision/detections", json.dumps(result))
    return result


@app.get("/api/detections")
def list_detections(limit: int = 20):
    items = list(detections)[-limit:]
    return {"count": len(items), "items": list(reversed(items))}
