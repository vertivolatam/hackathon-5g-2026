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
from fastapi.responses import HTMLResponse
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


def _trap_key(item: dict) -> str:
    """Deriva el id de trampa: payload.trap_id o último segmento del topic."""
    payload = item.get("payload") or {}
    if isinstance(payload, dict) and payload.get("trap_id"):
        return str(payload["trap_id"])
    return str(item.get("topic", "?")).rstrip("/").split("/")[-1]


def _latest_per_trap(items: list) -> list:
    """Última telemetría por trampa (recorre de más reciente a más vieja)."""
    seen: dict = {}
    for item in reversed(items):
        key = _trap_key(item)
        if key not in seen:
            seen[key] = item
    return [seen[k] for k in sorted(seen)]


def _admin_html() -> str:
    """Panel admin mínimo renderizado en servidor (sin dependencias nuevas)."""
    import html as _html
    import json as _json

    def esc(v) -> str:
        return _html.escape(str(v), quote=True)

    tele = list(store)[-20:]
    per_trap = _latest_per_trap(tele)
    dets = list(reversed(list(detections)[-20:]))
    rf_ok = rf_configured()
    mqtt_ok = mqtt_state.get("connected", False)

    tele_rows = "".join(
        f"<tr><td>{esc(_trap_key(t))}</td><td>{esc(t.get('topic'))}</td>"
        f"<td>{esc(t.get('ts'))}</td>"
        f"<td><code>{esc(_json.dumps(t.get('payload'), ensure_ascii=False)[:300])}</code></td></tr>"
        for t in reversed(per_trap)
    ) or '<tr><td colspan="4">sin datos</td></tr>'

    det_rows = ""
    for d in dets:
        preds = d.get("detections") or []
        pred_txt = ", ".join(
            f"{p.get('class')} ({p.get('confidence')})" for p in preds
        ) or "sin predicciones"
        det_rows += (
            f"<tr><td>{esc(d.get('trap_id'))}</td><td>{esc(d.get('ts'))}</td>"
            f"<td>{esc(d.get('model'))}</td><td>{esc(pred_txt)}</td></tr>"
        )
    det_rows = det_rows or '<tr><td colspan="4">sin datos</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="15">
<title>AgriVision · Panel admin</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%;margin-bottom:2rem}}
th,td{{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.9rem}}
th{{background:#f0f0f0}}
.ok{{color:green;font-weight:bold}}.bad{{color:red;font-weight:bold}}
</style>
</head>
<body>
<h1>AgriVision · Panel admin</h1>
<p>Auto-refresh cada 15 s.</p>
<h2>Estado</h2>
<ul>
<li>MQTT: <span class="{'ok' if mqtt_ok else 'bad'}">{'conectado' if mqtt_ok else 'desconectado'}</span>
{f" ({esc(mqtt_state.get('last_error'))})" if mqtt_state.get('last_error') else ''}</li>
<li>Roboflow configurado: <span class="{'ok' if rf_ok else 'bad'}">{'sí' if rf_ok else 'no'}</span></li>
<li>Telemetrías en buffer: {len(store)} · Detecciones en buffer: {len(detections)}</li>
</ul>
<h2>Última telemetría por trampa</h2>
<table><tr><th>Trampa</th><th>Topic</th><th>TS</th><th>Payload</th></tr>{tele_rows}</table>
<h2>Últimas detecciones (clase / confianza)</h2>
<table><tr><th>Trampa</th><th>TS</th><th>Modelo</th><th>Clase (confianza)</th></tr>{det_rows}</table>
<p><a href="/health">/health</a> · <a href="/api/telemetry">/api/telemetry</a> · <a href="/api/detections">/api/detections</a></p>
</body>
</html>"""


@app.get("/admin", response_class=HTMLResponse)
def admin():
    return _admin_html()
