# AgriVision — targets versionados para levantar todo el stack.
# Docker Compose (dev) y Minikube (cluster). `make help` lista todo.
#
#   make dev-full   -> backend + postgres + mosquitto + exporter + prometheus + grafana
#   make mk-all     -> lo mismo pero dentro de Minikube (incluye landing)

COMPOSE        := docker compose -f docker-compose.dev.yml
K8S_DIR        := backend/k8s
API_IMAGE      := agrivision-api:0.8.0
LANDING_IMAGE  := agrivision-landing:0.1.0
NAMESPACE      := agrivision
MINIKUBE_DRIVER ?= podman

.PHONY: help
help: ## Lista los targets disponibles
	@grep -E '^[a-z0-9-]+:.*?## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# --- Docker Compose (dev) -----------------------------------------------------

.PHONY: dev-up
dev-up: ## Backend + postgres + mosquitto (mínimo para la API)
	$(COMPOSE) up --build -d backend

.PHONY: dev-full
dev-full: ## TODO el stack dev: API + MQTT + exporter + Prometheus + Grafana
	$(COMPOSE) up --build -d
	@$(MAKE) dev-health

.PHONY: grafana-up
grafana-up: ## Solo Grafana (para incrustarlo en el HTML, ver docs how-to/grafana-embed)
	$(COMPOSE) up -d grafana
	@echo "Grafana: http://localhost:$${GRAFANA_PORT:-3000} (admin/admin)"

.PHONY: dev-ps
dev-ps: ## Estado de los contenedores dev
	$(COMPOSE) ps

.PHONY: dev-logs
dev-logs: ## Logs del stack dev (SERVICE=backend para filtrar)
	$(COMPOSE) logs -f $(SERVICE)

.PHONY: dev-health
dev-health: ## Chequea API, métricas, Prometheus, exporter y Grafana
	@echo "== API /health =="; curl -sf http://localhost:8000/health | head -c 400; echo
	@echo "== API /metrics =="; curl -sf http://localhost:8000/metrics | head -5
	@echo "== exporter :9234 =="; curl -sf http://localhost:9234/metrics | head -3
	@echo "== prometheus :9090 =="; curl -sf http://localhost:9090/-/healthy; echo
	@echo "== grafana :3000 =="; curl -sf http://localhost:3000/api/health; echo

.PHONY: smoke
smoke: ## Publica una telemetría MQTT de prueba y la lee vía API
	python3 -c "import paho.mqtt.publish as p; p.single('agrivision/trap-01', '{\"trap_id\":\"trap-01\"}', hostname='localhost', port=1883)"
	curl -s "http://localhost:8000/api/telemetry?limit=1"; echo

.PHONY: sim-trampa
sim-trampa: ## Simula la ESP32: telemetría MQTT + fotos + detect (TRAP_ID=trap-sim)
	TRAP_ID=$${TRAP_ID:-trap-sim} python3 scripts/sim_esp32.py --tele 5 --fotos 2

.PHONY: dev-down
dev-down: ## Apaga y borra el stack dev (con volúmenes: dev-nuke)
	$(COMPOSE) down

.PHONY: dev-nuke
dev-nuke: ## Apaga el stack dev BORRANDO volúmenes (datos de postgres/grafana)
	$(COMPOSE) down -v

# --- Imágenes Docker ----------------------------------------------------------

.PHONY: docker-build-backend
docker-build-backend: ## Construye la imagen del backend
	docker build --load -t $(API_IMAGE) backend/

.PHONY: docker-build-landing
docker-build-landing: ## Construye la imagen del landing
	docker build --load -t $(LANDING_IMAGE) landing/

.PHONY: docker-build-all
docker-build-all: docker-build-backend docker-build-landing ## Construye backend + landing

# --- Minikube (todo de una vez) ------------------------------------------------

.PHONY: mk-start
mk-start: ## Crea/enciende el cluster Minikube (MINIKUBE_DRIVER=podman por defecto)
	minikube start --driver=$(MINIKUBE_DRIVER) --cpus=2 --memory=4096

.PHONY: mk-build
mk-build: ## Construye las imágenes que usa el cluster (tags de backend/k8s/*.yaml)
	docker build --load -t $(API_IMAGE) backend/
	docker build --load -t $(LANDING_IMAGE) landing/

.PHONY: mk-load
mk-load: ## Carga las imágenes al cluster
	minikube image load $(API_IMAGE)
	minikube image load $(LANDING_IMAGE)

.PHONY: mk-apply
mk-apply: ## Aplica TODOS los manifests: API+MQTT+DB, monitoreo, landing e inference
	kubectl apply -f $(K8S_DIR)/agrivision.yaml
	kubectl apply -f $(K8S_DIR)/monitoring.yaml
	kubectl apply -f $(K8S_DIR)/landing.yaml
	kubectl apply -f $(K8S_DIR)/inference.yaml

.PHONY: mk-validate
mk-validate: ## Valida los manifests sin aplicarlos
	kubectl apply --dry-run=client -f $(K8S_DIR)/agrivision.yaml
	kubectl apply --dry-run=client -f $(K8S_DIR)/monitoring.yaml
	kubectl apply --dry-run=client -f $(K8S_DIR)/landing.yaml
	kubectl apply --dry-run=client -f $(K8S_DIR)/inference.yaml

.PHONY: mk-wait
mk-wait: ## Espera a que todos los deployments estén disponibles
	kubectl wait --for=condition=available deployment --all -n $(NAMESPACE) --timeout=300s

.PHONY: mk-status
mk-status: ## Muestra pods/servicios y NodePorts para entrar desde el host
	kubectl get pods,svc -n $(NAMESPACE)
	@echo "---"
	@echo "API:        minikube service api-external -n $(NAMESPACE)       (NodePort 30081)"
	@echo "MQTT:       minikube service mosquitto-external -n $(NAMESPACE) (NodePort 31883)"
	@echo "Prometheus: minikube service prometheus-external -n $(NAMESPACE) (NodePort 30090)"
	@echo "Grafana:    minikube service grafana-external -n $(NAMESPACE)   (NodePort 30300)"
	@echo "Landing:    minikube service landing-external -n $(NAMESPACE)   (NodePort 30080)"

.PHONY: mk-all
mk-all: mk-start mk-build mk-load mk-apply mk-wait mk-status ## TODO en Minikube de una vez

.PHONY: mk-clean
mk-clean: ## Borra los recursos del namespace (no borra el cluster)
	kubectl delete -f $(K8S_DIR)/inference.yaml --ignore-not-found
	kubectl delete -f $(K8S_DIR)/landing.yaml --ignore-not-found
	kubectl delete -f $(K8S_DIR)/monitoring.yaml --ignore-not-found
	kubectl delete -f $(K8S_DIR)/agrivision.yaml --ignore-not-found

# --- Firmware ESP32-P4-NANO (apps/esp-32) --------------------------------------

FW_PORT ?= /dev/ttyACM0

.PHONY: fw-check
fw-check: ## Espejo local del CI: py_compile + tests del firmware
	python3 -m py_compile apps/esp-32/*.py apps/esp-32/drivers/*.py
	python3 apps/esp-32/tests/test_smoke.py
	python3 apps/esp-32/tests/test_dispenser.py
	python3 apps/esp-32/tests/test_luz.py

.PHONY: fw-flash
fw-flash: ## Copia el firmware MicroPython a la placa (FW_PORT=/dev/ttyACM0)
	mpremote connect $(FW_PORT) cp -r apps/esp-32/boot.py apps/esp-32/main.py \
		apps/esp-32/config.py apps/esp-32/board.py apps/esp-32/drivers/ :

.PHONY: fw-ls
fw-ls: ## Lista archivos en la placa (verifica el flasheo)
	mpremote connect $(FW_PORT) ls

# --- Balena (gateway + esp-provisioner) ----------------------------------------

FLEET ?= org/fleet

.PHONY: balena-push
balena-push: ## Despliega gateway + esp-provisioner al fleet (FLEET=org/fleet)
	balena push $(FLEET) --source balena/

.PHONY: balena-provision
balena-provision: ## Provisiona la SD del gateway (pide FLEET/WIFI_KEY/BALENA_TOKEN)
	FLEET=$(FLEET) balena/balena.sh
