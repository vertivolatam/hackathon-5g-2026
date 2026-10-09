---
sidebar_position: 1
---

# Arquitectura

Objetivo (lo **planeado** va en línea punteada; el resto existe y corre).

```mermaid
graph TD
    T["Trampa ESP32-P4-NANO<br/>RG255C RedCap + AR1335/OV5647"] -->|MQTT telemetria<br/>por finca y trampa| NPN
    T -->|HTTP POST /api/fotos<br/>solo por evento| NPN
    G["Gateway Pi 4 + HAT RM520N-GL<br/>agent.py + comisionado"] -->|MQTT + fotos| NPN
    NPN["NPN privada 5G SA<br/>DNN por finca"] --> M
    NPN --> B
    M["Mosquitto<br/>ACL por trampa"] -->|subscribe| B["FastAPI<br/>ingest + fotos + proxy vision"]
    B --> S{"Modelo RF-DETR"}
    S --> C["Roboflow serverless"]
    S --> L["Inference local"]
    C --> D[["MQTT detecciones y alertas"]]
    L --> D
    B -->|bytea + metadatos| P[("PostgreSQL")]
    B -->|/metrics| PR["Prometheus"]
    PR --> GR["Grafana<br/>metricas + fotos Base64"]
    D --> APIV["API + landing"]
    D --> TG["Telegram<br/>foto + caption"]
    D -. canal productor (planeado) .-> WA["WhatsApp / correo"]
    CEL["Tecnico / productor"] --> APIV
    GR -. iframe d-solo .-> APIV

    classDef planeado stroke-dasharray:5 5;
    class WA planeado;
```

Flujo de la demo hoy (UML secuencia):

```mermaid
sequenceDiagram
    participant T as Trampa RedCap
    participant M as Mosquitto
    participant B as FastAPI
    participant P as Postgres
    participant R as RF-DETR
    participant GR as Grafana
    T->>M: telemetria por finca y trampa
    T->>B: POST /api/fotos (multipart, por evento)
    B->>P: bytea + metadatos
    B->>R: inferencia sobre la foto
    R-->>B: predicciones + cajas
    B->>M: publish detecciones y alertas
    GR->>P: ultima foto en base64 (panel Business Media)
```

Decisiones clave (detalle en `docs/vision-rf-detr.md` del repo):

- **El modelo corre en la nube, no en el edge**: RF-DETR necesita GPU/CPU seria.
- **Mismo código, dos rutas**: `ROBOFLOW_URL` conmuta serverless ↔ self-hosted sin cambiar nada.
- **Backend proxea la key**: nunca va en el frontend ni en el firmware.
- **Degradado limpio**: sin keys, `/api/detect` da 503 y el resto sigue vivo.

## Brechas (roadmap jurado-ready)

| # | Brecha | Qué falta | Desbloquea |
|---|---|---|---|
| 1 | Persistencia ✅ | Postgres + TimescaleDB (hypertables en `telemetry`/`detections`, modelos SQLAlchemy intactos); sobrevive rollouts | Historial, tendencias, métricas honestas |
| 2 | Observabilidad ✅ | `/metrics` + Prometheus + Grafana corriendo; panel de fotos con plugin Business Media | Latencia captura→alerta, SLOs del piloto |
| 3 | Dashboard | Mapa + historial + prioridad (hoy landing + Grafana + API cruda) | El producto que la bitácora promete |
| 4 | Cámara CSI | Sin driver CSI en 2026 (solo probe SCCB); OV5647 valida el pipeline, AR1335 vía adaptador | Detección real en trampa |
| 5 | Telegram ✅ / WhatsApp pendiente | Bot push con foto ante broca (`notify.py`); falta reenvío a WhatsApp/correo | Canal que los entrevistados pidieron |
