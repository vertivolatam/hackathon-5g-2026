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
from db import (
    SessionLocal,
    TelemetryItem,
    Detection,
    Cooperativa,
    Finca,
    Tecnico,
    Visita,
    Incidencia,
    init_db,
)

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "agrivision/#")

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


# ---------- CRUD genérico sobre modelos SQLAlchemy ----------
MODELOS = {
    "cooperativas": Cooperativa,
    "fincas": Finca,
    "tecnicos": Tecnico,
    "visitas": Visita,
    "incidencias": Incidencia,
}


def _a_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _registrar_crud(nombre, modelo):
    @app.get(f"/api/{nombre}")
    def listar(cooperativaId: str | None = None, limit: int = 200):
        db = SessionLocal()
        try:
            q = db.query(modelo)
            if cooperativaId and hasattr(modelo, "cooperativaId"):
                q = q.filter(modelo.cooperativaId == cooperativaId)
            return {"count": q.count(), "items": [_a_dict(x) for x in q.limit(limit).all()]}
        finally:
            db.close()

    @app.post(f"/api/{nombre}", status_code=201)
    def crear(body: dict):
        db = SessionLocal()
        try:
            obj = modelo(**{k: v for k, v in body.items() if hasattr(modelo, k)})
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return _a_dict(obj)
        finally:
            db.close()

    @app.put(f"/api/{nombre}/{{item_id}}")
    def actualizar(item_id: str, body: dict):
        db = SessionLocal()
        try:
            obj = db.get(modelo, item_id)
            if not obj:
                raise HTTPException(status_code=404, detail="no encontrado")
            for k, v in body.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
            db.commit()
            db.refresh(obj)
            return _a_dict(obj)
        finally:
            db.close()

    @app.delete(f"/api/{nombre}/{{item_id}}", status_code=204)
    def eliminar(item_id: str):
        db = SessionLocal()
        try:
            obj = db.get(modelo, item_id)
            if not obj:
                raise HTTPException(status_code=404, detail="no encontrado")
            db.delete(obj)
            db.commit()
        finally:
            db.close()
        return None


for _nombre, _modelo in MODELOS.items():
    _registrar_crud(_nombre, _modelo)


def _record(topic: str, payload, raw: str | None = None):
    db = SessionLocal()
    try:
        item = TelemetryItem(topic=topic, payload=payload, raw=raw)
        db.add(item)
        db.commit()
        db.refresh(item)
        return {
            "topic": item.topic,
            "payload": item.payload,
            "raw": item.raw,
            "ts": item.ts.isoformat() if item.ts else None,
        }
    finally:
        db.close()


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
    init_db()
    t = threading.Thread(target=_mqtt_loop, daemon=True)
    t.start()


@app.get("/health")
def health():
    return {
        "status": "ok",
        **mqtt_state,
        "buffered": SessionLocal().query(TelemetryItem).count(),
        "detections": SessionLocal().query(Detection).count(),
        "roboflow": {"configured": rf_configured()},
    }


@app.get("/api/telemetry")
def list_telemetry(limit: int = 20):
    db = SessionLocal()
    try:
        items = db.query(TelemetryItem).order_by(TelemetryItem.id.desc()).limit(limit).all()
        return {
            "count": len(items),
            "items": [
                {"topic": i.topic, "payload": i.payload, "raw": i.raw, "ts": i.ts.isoformat() if i.ts else None}
                for i in items
            ],
        }
    finally:
        db.close()


@app.get("/api/telemetry/latest")
def latest():
    db = SessionLocal()
    try:
        item = db.query(TelemetryItem).order_by(TelemetryItem.id.desc()).first()
        if not item:
            raise HTTPException(status_code=404, detail="sin datos")
        return {"topic": item.topic, "payload": item.payload, "raw": item.raw, "ts": item.ts.isoformat() if item.ts else None}
    finally:
        db.close()


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
    db = SessionLocal()
    try:
        d = Detection(trap_id=body.trap_id, model=result["model"], detections=preds)
        db.add(d)
        db.commit()
    finally:
        db.close()
    if body.publish_mqtt and _mqtt_client and mqtt_state["connected"]:
        _mqtt_client.publish("agrivision/detections", json.dumps(result))
    return result


@app.get("/api/detections")
def list_detections(limit: int = 20):
    db = SessionLocal()
    try:
        items = db.query(Detection).order_by(Detection.id.desc()).limit(limit).all()
        return {
            "count": len(items),
            "items": [
                {"trap_id": d.trap_id, "model": d.model, "detections": d.detections, "ts": d.ts.isoformat() if d.ts else None}
                for d in items
            ],
        }
    finally:
        db.close()
