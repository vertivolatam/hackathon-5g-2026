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
docker build --load -t agrivision-api:0.6.0 backend/
minikube image load docker.io/library/agrivision-api:0.6.0
kubectl apply -f backend/k8s/agrivision.yaml
kubectl wait --for=condition=ready pod -l app=agrivision-api -n agrivision --timeout=120s
kubectl wait --for=condition=ready pod -l app=mosquitto -n agrivision --timeout=120s
```

> Atajo: `make mk-all` hace todo de una vez (cluster + imágenes + los tres
> manifests + espera), incluyendo monitoreo y landing (ver siguiente sección).

## 1b. Monitoreo y landing (Prometheus + Grafana + web)

```bash
kubectl apply -f backend/k8s/monitoring.yaml
kubectl apply -f backend/k8s/landing.yaml
kubectl wait --for=condition=available deployment --all -n agrivision --timeout=300s
make mk-status   # muestra los NodePorts: API 30081, MQTT 31883, Prometheus 30090, Grafana 30300, landing 30080
```

Prometheus scrapea la API (`/metrics`) y al exporter del broker MQTT.
Grafana permite incrustación por iframe: ver [Incrustar Grafana](../how-to/grafana-embed).

## 2. Puertos al host

```bash
kubectl port-forward svc/api 8001:8000 -n agrivision &
kubectl port-forward svc/mosquitto 1883:1883 -n agrivision &
curl -s localhost:8001/health
```

## 3. Prueba de telemetría

```bash
python3 -c "import paho.mqtt.publish as p; p.single('agrivision/trap-01', '{\"trap_id\":\"trap-01\"}', hostname='localhost', port=1883)"
curl -s "localhost:8001/api/telemetry?limit=1"
```

## 4. Túneles públicos

Ver [Túnel Cloudflare](../how-to/tunel-cloudflare).

## Siguiente paso

Conseguir cajas reales de broca: [Keys y modelo Roboflow](../how-to/roboflow-keys).
