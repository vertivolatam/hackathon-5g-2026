---
sidebar_position: 1
---

# Arquitectura

Objetivo (no todo existe hoy: lo **planeado** va en línea punteada).

```mermaid
graph TD
    T["Trampa ESP32-P4-NANO (existe)<br/>OV5647 PoC / AR1335 final + MQTT"] -->|agrivision/telemetry| N5
    G["Gateway Pi 4 + HAT RM520N-GL (existe)<br/>agent.py: foto + telemetría"] -->|agrivision/telemetry| N5
    G -->|POST /api/detect<br/>foto base64| N5
    N5["5G sub-6 (piloto)"] --> M
    N5 --> B
    M["Mosquitto (existe)<br/>topics agrivision/#"] -->|subscribe| B["FastAPI (existe)<br/>ingest + proxy visión"]
    B --> S{"Modelo RF-DETR"}
    S --> C["Nube Roboflow (existe con keys)<br/>serverless"]
    S --> L["Inference Server local (probado)<br/>RTX laptop"]
    C --> D[["agrivision/detections"]]
    L --> D
    B -->|persiste evento| P[("PostgreSQL + TimescaleDB (existe)")]
    B -. expone /metrics (planeado) .-> PR["Prometheus (planeado)"]
    PR --> GR["Grafana (planeado)"]
    D --> APIV["API pública + landing (existe)"]
    D -. reenvía gateway (planeado) .-> WA["WhatsApp / correo (planeado)<br/>alertas al técnico"]
    CEL["Celular técnico / productor"] --> APIV
    DASH["Dashboard AgriVision (planeado)<br/>mapa + historial + prioridad"] -. lee .-> P
    DASH -. lee .-> APIV

    classDef planeado stroke-dasharray:5 5;
    class PR,GR,WA,DASH planeado;
```

Flujo de la demo hoy (UML secuencia, todo existe salvo persistencia):

```mermaid
sequenceDiagram
    participant T as Trampa ESP32
    participant G as Gateway Pi
    participant M as Mosquitto
    participant B as FastAPI
    participant R as RF-DETR
    T->>M: agrivision/telemetry (sensores)
    G->>B: POST /api/detect (foto base64)
    B->>R: multipart + Authorization Bearer
    R-->>B: predicciones + cajas
    B->>M: publish agrivision/detections
    B-->>M: (planeado) persiste evento en Postgres
    G->>M: publish agrivision/alertas (si ≥ umbral)
```

Decisiones clave (detalle en `docs/vision-rf-detr.md` del repo):

- **El modelo corre en la nube, no en el edge**: RF-DETR necesita GPU/CPU seria.
- **Mismo código, dos rutas**: `ROBOFLOW_URL` conmuta serverless ↔ self-hosted sin cambiar nada.
- **Backend proxea la key**: nunca va en el frontend ni en el firmware.
- **Degradado limpio**: sin keys, `/api/detect` da 503 y el resto sigue vivo.

## Brechas (roadmap jurado-ready)

| # | Brecha | Qué falta | Desbloquea |
|---|---|---|---|
| 1 | Persistencia ✅ | Postgres+Timescale con hypertables (StatefulSet 5Gi); sobrevive rollouts | Historial, tendencias, métricas honestas |
| 2 | Observabilidad | `/metrics` + Prometheus + Grafana | Latencia captura→alerta, SLOs del piloto |
| 3 | Dashboard | Mapa + historial + prioridad (hoy solo landing + API cruda) | El producto que la bitácora promete |
| 4 | Cámara CSI | Sin driver CSI en 2026 (solo probe SCCB); validar lente 8–12 mm a 10–20 cm | Detección real en trampa |
| 5 | WhatsApp | Reenvío gateway → WhatsApp/correo | Canal que los entrevistados pidieron |
