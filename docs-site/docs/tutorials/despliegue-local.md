---
sidebar_position: 1
---

# Despliegue local completo

Levanta todo el stack en esta laptop: cluster, broker, backend y túneles.
Al final tienes telemetría MQTT entrando y API pública. Tiempo estimado: ~15 min.

## Requisitos

- `kubectl` + `minikube` (driver podman) · `python3` · `cloudflared` en `~/.local/bin`

## 1. Cluster y backend

```bash
minikube start --driver=podman --cpus=2 --memory=4096
docker build --load -t biotrap-api:0.5.0 backend/
minikube image load docker.io/library/biotrap-api:0.5.0
kubectl apply -f backend/k8s/biotrap.yaml
kubectl wait --for=condition=ready pod -l app=biotrap-api -n biotrap --timeout=120s
kubectl wait --for=condition=ready pod -l app=mosquitto -n biotrap --timeout=120s
```

## 2. Puertos al host

```bash
kubectl port-forward svc/api 8001:8000 -n biotrap &
kubectl port-forward svc/mosquitto 1883:1883 -n biotrap &
curl -s localhost:8001/health
```

## 3. Prueba de telemetría

```bash
python3 -c "import paho.mqtt.publish as p; p.single('biotrap/trap-01', '{\"trap_id\":\"trap-01\"}', hostname='localhost', port=1883)"
curl -s "localhost:8001/api/telemetry?limit=1"
```

## 4. Túneles públicos

Ver [Túnel Cloudflare](../how-to/tunel-cloudflare).

## Siguiente paso

Conseguir cajas reales de broca: [Keys y modelo Roboflow](../how-to/roboflow-keys).
