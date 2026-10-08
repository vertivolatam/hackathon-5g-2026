"""AgriVision backend: ingest MQTT (agrivision/#) y expone HTTP para la landing."""
import json
import os
import threading
import time
from collections import deque
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from fastapi import FastAPI, File, Form, Header, HTTPException, Depends, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from pydantic import BaseModel

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

    _PROM = True
    TELEMETRY_TOTAL = Counter(
        "agrivision_telemetry_ingested_total",
        "Telemetrías MQTT ingeridas por la API.",
    )
    DETECTIONS_TOTAL = Counter(
        "agrivision_detections_total",
        "Resultados de /api/detect publicados.",
    )
    MQTT_CONNECTED = Gauge(
        "agrivision_mqtt_connected",
        "1 si el cliente MQTT está conectado al broker, 0 si no.",
    )
    DB_OK = Gauge(
        "agrivision_postgres_ok",
        "1 si la última operación Postgres funcionó, 0 si no.",
    )
    BUFFER_SIZE = Gauge(
        "agrivision_buffer_size",
        "Telemetrías retenidas en el buffer en memoria.",
    )
    FOTOS_TOTAL = Counter(
        "agrivision_fotos_total",
        "Fotos recibidas en POST /api/fotos, por trampa.",
        ["trap_id"],
    )
    FOTO_BYTES = Gauge(
        "agrivision_foto_bytes",
        "Tamaño en bytes de la última foto, por trampa.",
        ["trap_id"],
    )
    TRAP_RSSI = Gauge(
        "agrivision_trap_rssi_dbm",
        "RSSI del módem 5G reportado por la trampa en su telemetría.",
        ["trap_id"],
    )
except ImportError:  # sin prometheus-client: /metrics responde 503
    _PROM = False

from vision import configured as rf_configured
from vision import detect_b64 as rf_detect
import notify
from db import (
    SessionLocal,
    TelemetryItem,
    Detection,
    Foto,
    Cooperativa,
    Finca,
    Tecnico,
    Visita,
    Incidencia,
    Usuario,
    init_db,
)
from auth import LoginIn, verificar_password, crear_token, usuario_actual, hash_password

import db

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "agrivision/#")

# Clases que disparan alerta (intercambiables por plaga sin tocar código).
ALERT_CLASSES = set(os.getenv("ALERT_CLASSES", "broca").split(","))
ALERT_MIN_CONF = float(os.getenv("ALERT_MIN_CONF", "0.5"))

mqtt_state = {"connected": False, "last_error": None}
_mqtt_client = None

# Buffers en memoria para el panel /admin (la fuente de verdad es Postgres).
MAX_ITEMS = 200
store: deque = deque(maxlen=MAX_ITEMS)
detections: deque = deque(maxlen=MAX_ITEMS)

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
    def listar(cooperativaId: str | None = None, limit: int = 200, usuario: dict = Depends(usuario_actual)):
        db = SessionLocal()
        try:
            q = db.query(modelo)
            if cooperativaId and hasattr(modelo, "cooperativaId"):
                q = q.filter(modelo.cooperativaId == cooperativaId)
            return {"count": q.count(), "items": [_a_dict(x) for x in q.limit(limit).all()]}
        finally:
            db.close()

    @app.post(f"/api/{nombre}", status_code=201)
    def crear(body: dict, usuario: dict = Depends(usuario_actual)):
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
    def actualizar(item_id: str, body: dict, usuario: dict = Depends(usuario_actual)):
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
    def eliminar(item_id: str, usuario: dict = Depends(usuario_actual)):
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


@app.post("/api/auth/login")
def login(body: LoginIn):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == body.email).first()
        if not usuario or not verificar_password(body.password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        return {
            "token": crear_token(usuario),
            "email": usuario.email,
            "rol": usuario.rol,
            "cooperativaId": usuario.cooperativaId,
        }
    finally:
        db.close()


def _record(topic: str, payload, raw: str | None = None):
    db = SessionLocal()
    try:
        item = TelemetryItem(topic=topic, payload=payload, raw=raw)
        db.add(item)
        db.commit()
        db.refresh(item)
        out = {
            "topic": item.topic,
            "payload": item.payload,
            "raw": item.raw,
            "ts": item.ts.isoformat() if item.ts else None,
        }
        store.append(out)
        if _PROM:
            TELEMETRY_TOTAL.inc()
            try:
                rssi = float(payload.get("rssi_dbm")) if isinstance(payload, dict) else None
                if rssi is not None:
                    tid = payload.get("trap_id") or out["topic"].rstrip("/").split("/")[-1]
                    TRAP_RSSI.labels(trap_id=str(tid)).set(rssi)
            except (TypeError, ValueError, AttributeError):
                pass
        return out
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


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """Métricas Prometheus (API + estado MQTT/DB). Las scrapea Prometheus."""
    if not _PROM:
        raise HTTPException(
            status_code=503, detail="prometheus-client no instalado"
        )
    MQTT_CONNECTED.set(1 if mqtt_state["connected"] else 0)
    try:
        SessionLocal().query(TelemetryItem).count()
        DB_OK.set(1)
    except Exception:
        DB_OK.set(0)
    BUFFER_SIZE.set(len(store))
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
    detections.append(result)
    if _PROM:
        DETECTIONS_TOTAL.inc()
    notify.alert_if_needed(
        body.trap_id,
        result["model"],
        preds,
        body.image_base64,
        classes=ALERT_CLASSES,
        min_conf=ALERT_MIN_CONF,
    )
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


FOTO_API_KEY = os.getenv("FOTO_API_KEY", "")
FOTO_MAX_BYTES = int(os.getenv("FOTO_MAX_BYTES", str(10 * 1024 * 1024)))


def _check_trap_key(x_trap_key: str | None):
    """Auth de trampas para subir fotos (header X-Trap-Key).

    Si FOTO_API_KEY está vacío (dev) se permite todo con warning en log;
    en campo es obligatoria y el backend responde 401 sin ella.
    """
    if not FOTO_API_KEY:
        print("WARN: FOTO_API_KEY vacío, subida de fotos abierta (solo dev)")
        return
    if x_trap_key != FOTO_API_KEY:
        raise HTTPException(status_code=401, detail="X-Trap-Key inválido")


def _foto_meta(f):
    return {
        "id": f.id,
        "trap_id": f.trap_id,
        "filename": f.filename,
        "content_type": f.content_type,
        "size_bytes": f.size_bytes,
        "ts": f.ts.isoformat() if f.ts else None,
    }


@app.post("/api/fotos", status_code=201)
async def subir_foto(
    file: UploadFile = File(...),
    trap_id: str = Form("trap-01"),
    x_trap_key: str | None = Header(default=None),
):
    """Sube la foto de una trampa (multipart, solo por evento).

    Guarda binario (bytea) + metadatos en Postgres, publica el evento
    `agrivision/<trap_id>/foto` en MQTT (JSON con id/ts/tamaño, sin
    bytes) y cuenta en Prometheus. Grafana la lee con encode() + panel
    Business Media (ver docs reference/fotos-pipeline).
    """
    _check_trap_key(x_trap_key)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="archivo vacío")
    if len(data) > FOTO_MAX_BYTES:
        raise HTTPException(status_code=413, detail="foto supera FOTO_MAX_BYTES")
    content_type = file.content_type or "image/jpeg"
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="solo image/*")
    db = SessionLocal()
    try:
        f = Foto(
            trap_id=trap_id,
            filename=file.filename or "foto.jpg",
            content_type=content_type,
            size_bytes=len(data),
            data=data,
        )
        db.add(f)
        db.commit()
        db.refresh(f)
        meta = _foto_meta(f)
    finally:
        db.close()
    if _PROM:
        FOTOS_TOTAL.labels(trap_id=trap_id).inc()
        FOTO_BYTES.labels(trap_id=trap_id).set(len(data))
    if _mqtt_client and mqtt_state["connected"]:
        _mqtt_client.publish(
            f"agrivision/{trap_id}/foto",
            json.dumps({"foto_id": meta["id"], "ts": meta["ts"], "size_bytes": meta["size_bytes"]}),
        )
    return meta


@app.get("/api/fotos")
def listar_fotos(trap_id: str | None = None, limit: int = 20):
    """Metadatos de fotos (sin binario), más recientes primero."""
    db = SessionLocal()
    try:
        q = db.query(Foto).order_by(Foto.id.desc())
        if trap_id:
            q = q.filter(Foto.trap_id == trap_id)
        items = q.limit(max(limit, 1)).all()
        return {"count": len(items), "items": [_foto_meta(f) for f in items]}
    finally:
        db.close()


def _foto_or_404(db, foto_id: int):
    f = db.get(Foto, foto_id)
    if not f:
        raise HTTPException(status_code=404, detail="foto no encontrada")
    return f


@app.get("/api/fotos/latest")
def ultima_foto(trap_id: str):
    """Última foto de una trampa (bytes). 404 si no hay."""
    db = SessionLocal()
    try:
        f = (
            db.query(Foto)
            .filter(Foto.trap_id == trap_id)
            .order_by(Foto.id.desc())
            .first()
        )
        if not f:
            raise HTTPException(status_code=404, detail="sin fotos de esa trampa")
        return Response(content=f.data, media_type=f.content_type)
    finally:
        db.close()


@app.get("/api/fotos/{foto_id}")
def ver_foto(foto_id: int):
    """Bytes de la foto (para <img> o descarga)."""
    db = SessionLocal()
    try:
        f = _foto_or_404(db, foto_id)
        return Response(content=f.data, media_type=f.content_type)
    finally:
        db.close()


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
