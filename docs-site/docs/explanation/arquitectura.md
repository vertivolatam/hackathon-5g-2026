---
sidebar_position: 1
---

# Arquitectura

```
trampa ESP32 (MicroPython, MQTT) ─┐
gateway Pi (Python, fotos) ───────┼─→ Mosquitto ─→ FastAPI ─→ RF-DETR (nube Roboflow)
                                                   │                 (o Inference Server local)
                                                   └→ MQTT agrivision/detections → landing/API pública
```

Decisiones clave (detalle en `docs/vision-rf-detr.md` del repo):

- **El modelo corre en la nube**, no en el edge: RF-DETR necesita GPU/CPU seria.
- **Mismo código, dos rutas**: `ROBOFLOW_URL` conmuta serverless ↔ self-hosted sin cambiar nada.
- **Backend proxea la key**: nunca va en el frontend ni en el firmware.
- **Degradado limpio**: sin keys, `/api/detect` da 503 y el resto sigue vivo.
