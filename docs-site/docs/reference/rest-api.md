---
sidebar_position: 2
---

# REST + OpenAPI

Referencia interactiva generada del backend (Redoc): **[API Redoc](https://vertivolatam.github.io/hackathon-5g-2026/docs/api/)**.

- `GET /health` — estado + MQTT + `roboflow.configured`.
- `GET /api/telemetry?limit=N` — últimas N telemetrías.
- `GET /api/telemetry/latest` — última (404 si vacío).
- `POST /api/telemetry` — ingest directo `{topic, payload}`.
- `POST /api/detect` — `{trap_id, image_base64, publish_mqtt}` → cajas RF-DETR; 400 sin imagen, 503 sin keys, 502 si falla Roboflow.
- `GET /api/detections?limit=N` — historial de detecciones.

El `openapi.json` se exporta del código en cada build (`backend/scripts/export_openapi.py`), así que esta referencia nunca deriva del implementado.
