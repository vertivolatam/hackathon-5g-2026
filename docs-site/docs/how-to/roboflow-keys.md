---
sidebar_position: 2
---

# Keys y modelo Roboflow

Sin API key, `POST /api/detect` responde 503 (correcto: el backend degrada sin keys).

## Default: self-hosted en Minikube (demo)

`make mk-apply` levanta el Inference Server CPU (`backend/k8s/inference.yaml`) y el backend ya apunta ahí (`ROBOFLOW_URL` al servicio `inference:9001`). La API key sigue siendo obligatoria: el servidor la usa para descargar el modelo.

```bash
kubectl -n agrivision create secret generic roboflow --from-literal=api-key='TU_API_KEY'
kubectl apply -f backend/k8s/inference.yaml
kubectl apply -f backend/k8s/agrivision.yaml
```

Imagen pesada (varios GB): hacer pull la noche antes (`docker pull roboflow/roboflow-inference-server-cpu:latest` + `minikube image load`).

## Opt-in: serverless cloud

Solo si hay internet y prefieres no correr el servidor: `ROBOFLOW_URL=https://serverless.roboflow.com` en el Deployment (o en compose dev). Mismo `MODEL_ID`, sin más cambios.

## 1. Dataset y entrenamiento (una vez, en tu cuenta)

1. Fork de `universe.roboflow.com/ralph-matthew-r-aquino/coffee-berry-borer` (1.9k fotos, CC BY 4.0).
2. Train RF-DETR (notebook de fine-tuning o Roboflow Train).
3. Deploy → anota el `MODEL_ID` (`tu-workspace/coffee-berry-borer/1`).

Ojo: son fotos close-up; valida en tu cafetal bajo sombra (el 0.94 de lab cayó a 0.73 en campo según la literatura).

## 2. Cablear al cluster

```bash
kubectl -n agrivision create secret generic roboflow --from-literal=api-key='TU_API_KEY'
# ROBOFLOW_MODEL_ID va en backend/k8s/agrivision.yaml (env del Deployment api).
# ROBOFLOW_URL ya apunta al inference self-hosted por defecto.
kubectl apply -f backend/k8s/agrivision.yaml
kubectl rollout status deploy/api -n agrivision
```

En compose dev el inference es opt-in: `docker compose --profile inference up -d` + `ROBOFLOW_URL=http://inference:9001`.

## 3. Verificar

```bash
curl -s localhost:8001/health  # roboflow.configured debe ser true
curl -X POST localhost:8001/api/detect -H 'Content-Type: application/json' \
  -d "{\"trap_id\":\"trap-01\",\"image_base64\":\"$(base64 -w0 foto-campo.jpg)\"}"
```

Alternativa sin nube: `ROBOFLOW_URL=http://localhost:9001` contra Inference Server self-hosted.

## Cambiar de plaga/enfermedad (sin tocar código)

El backend es agnóstico al modelo: solo cambian 3 variables (ver `backend/tests/test_vision_swap.py`, que lo demuestra con roya sin red):

| Variable | Ejemplo broca | Ejemplo roya | Dónde |
|---|---|---|---|
| `ROBOFLOW_MODEL_ID` | `tu-ws/coffee-berry-borer/1` | `tu-ws/roya-cafe/3` | compose / `agrivision.yaml` |
| `ALERT_CLASSES` | `broca` | `roya,ojo-de-gallo` | compose / `agrivision.yaml` (coma-separado) |
| `ALERT_MIN_CONF` | `0.5` | `0.6` | compose / `agrivision.yaml` |

El `model_id` fluye a la respuesta, la DB, MQTT y el caption de Telegram; las clases fuera de `ALERT_CLASSES` se registran pero no alertan.
