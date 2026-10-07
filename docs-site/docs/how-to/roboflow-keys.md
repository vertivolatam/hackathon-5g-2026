---
sidebar_position: 2
---

# Keys y modelo Roboflow

Sin esto, `POST /api/detect` responde 503 (correcto: el backend degrada sin keys).

## 1. Dataset y entrenamiento (una vez, en tu cuenta)

1. Fork de `universe.roboflow.com/ralph-matthew-r-aquino/coffee-berry-borer` (1.9k fotos, CC BY 4.0).
2. Train RF-DETR (notebook de fine-tuning o Roboflow Train).
3. Deploy → anota el `MODEL_ID` (`tu-workspace/coffee-berry-borer/1`).

Ojo: son fotos close-up; valida en tu cafetal bajo sombra (el 0.94 de lab cayó a 0.73 en campo según la literatura).

## 2. Cablear al cluster

```bash
kubectl -n agrivision create secret generic roboflow --from-literal=api-key='TU_API_KEY'
# ROBOFLOW_MODEL_ID va en backend/k8s/agrivision.yaml (env del Deployment api)
kubectl apply -f backend/k8s/agrivision.yaml
kubectl rollout status deploy/api -n agrivision
```

## 3. Verificar

```bash
curl -s localhost:8001/health  # roboflow.configured debe ser true
curl -X POST localhost:8001/api/detect -H 'Content-Type: application/json' \
  -d "{\"trap_id\":\"trap-01\",\"image_base64\":\"$(base64 -w0 foto-campo.jpg)\"}"
```

Alternativa sin nube: `ROBOFLOW_URL=http://localhost:9001` contra Inference Server self-hosted.
