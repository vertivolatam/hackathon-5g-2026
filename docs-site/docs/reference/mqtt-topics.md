---
sidebar_position: 1
---

# Tópicos MQTT

Contrato del broker (Mosquitto). Fuente de verdad del productor: `backend/app.py`, `balena/gateway/agent.py`, `apps/esp-32/`. Detalle del pipeline de fotos: [fotos-pipeline](./fotos-pipeline).

Árbol por finca (el `device-id` va en el tópico, nunca en el DNN):

| Tópico | Productor | Contenido |
|---|---|---|
| `agrivision/<cli>/<finca>/<trampa>/telemetry` | ESP32 / gateway | JSON sensores `{trap_id, temp_c, hum_pct, count, ts}` |
| `agrivision/<cli>/<finca>/<trampa>/foto` | backend | Evento de foto `{foto_id, ts, size_bytes}` (**sin bytes**; el binario va por `POST /api/fotos`) |
| `agrivision/<cli>/<finca>/<trampa>/detections` | backend | Resultado RF-DETR `{trap_id, model, detections:[{class, confidence, bbox}], ts}` |
| `agrivision/<cli>/<finca>/<trampa>/alertas` | gateway | Detecciones sobre umbral (`ALERT_CLASSES`, `ALERT_MIN_CONF`) |
| `agrivision/<cli>/<finca>/<trampa>/estado` | trampa (LWT) | birth/will: online/offline + batería |
| `agrivision/<cli>/<finca>/<trampa>/cmd` | plataforma | Downlink: captura ya, cambia ciclo, reinicia |

Compatibilidad: los tópicos planos viejos (`agrivision/telemetry`, `agrivision/detections`, `agrivision/<trap>/foto`) se siguen publicando/leyendo durante la migración.

Notas:

- El backend **ignora** `*/detections` en su ingest (es su propio tópico de salida).
- Clases: `broca` prioritaria. Umbral default `0.4` (calibrar en campo 0.3–0.5).
- Broker anónimo (demo). Antes de campo: auth por usuario-trampa + TLS, ACL por subárbol `agrivision/<cli>/<finca>/<trampa>/#`, y cerrar NodePorts.
