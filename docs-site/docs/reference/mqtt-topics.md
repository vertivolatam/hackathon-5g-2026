---
sidebar_position: 1
---

# Tópicos MQTT

Contrato del broker (Mosquitto, `agrivision/#`). Fuente de verdad del productor: `backend/app.py`, `balena/gateway/agent.py`.

| Tópico | Productor | Contenido |
|---|---|---|
| `agrivision/telemetry` | ESP32 / gateway | JSON sensores `{trap_id, temp_c, hum_pct, count, ts}` |
| `agrivision/detections` | backend | Resultado RF-DETR `{trap_id, model, detections:[{class, confidence, bbox}], ts}` |
| `agrivision/alertas` | gateway | Detecciones sobre umbral (`ALERT_CLASSES`, `ALERT_MIN_CONF`) |

Notas:

- El backend **ignora** `agrivision/detections` en su ingest (es su propio tópico de salida).
- Clases: `broca` prioritaria. Umbral default `0.4` (calibrar en campo 0.3–0.5).
- Broker anónimo (demo). Antes de campo: auth + TLS y cerrar NodePorts.
