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

.PHONY: dev-backend
dev-backend: dev-up ## Alias explícito: solo el backend y sus dependencias

.PHONY: dev-landing
dev-landing: ## Solo la landing page pública (nginx :8080)
	$(COMPOSE) up --build -d landing
	@echo "Landing: http://localhost:$${LANDING_PORT:-8080}"

.PHONY: dev-admin
dev-admin: ## Solo la consola de administración (Grafana + Prometheus + exporter)
	$(COMPOSE) up -d grafana
	@echo "Grafana: http://localhost:$${GRAFANA_PORT:-3000} (admin/admin)"

.PHONY: dev-full
dev-full: ## TODO el stack dev: backend + landing + admin (Grafana/Prometheus)
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

.PHONY: sim-edge-trampa
sim-edge-trampa: ## Trampa real: captura con UI (MIPI > Streamplify > integrada) + telemetría + fotos (PREVIEW=1, ANNOTATE=1 con keys)
	TRAP_ID=$${TRAP_ID:-trap-edge} CAM_ORDER=$${CAM_ORDER:-mipi,usb:streamplify,usb:any} python3 scripts/sim_esp32.py --tele 2 --fotos 1 --cam $${FOTO:+--foto $${FOTO}} $${PREVIEW:+--preview} $${ANNOTATE:+--annotate}

.PHONY: cam-consola
cam-consola: ## Consola Qt de trampa (dropdown de cámara + Detectar + veredicto). Requiere ~/.venv/qt
	QT_QPA_PLATFORM=xcb ~/.venv/qt/bin/python scripts/cam_consola.py

.PHONY: cam-venv
cam-venv: ## Crea ~/.venv/qt con PySide6 + OpenCV (persiste reboots, fuera de /tmp)
	python3 -m venv ~/.venv/qt && ~/.venv/qt/bin/pip install PySide6 opencv-python Pillow paho-mqtt

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
mk-apply: mk-backend mk-monitoreo mk-landing mk-inference ## TODO en Minikube por bloques

.PHONY: mk-backend
mk-backend: ## Bloque backend: API + MQTT + Postgres (agrivision.yaml)
	kubectl apply -f $(K8S_DIR)/agrivision.yaml

.PHONY: mk-monitoreo
mk-monitoreo: ## Bloque monitoreo: Prometheus + exporter + Grafana admin
	kubectl apply -f $(K8S_DIR)/monitoring.yaml

.PHONY: mk-landing
mk-landing: ## Bloque landing page pública
	kubectl apply -f $(K8S_DIR)/landing.yaml

.PHONY: mk-inference
mk-inference: ## Bloque inference self-hosted (pesado: pull aparte)
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
	@kubectl -n $(NAMESPACE) get statefulset postgres -o jsonpath='Postgres: {.status.readyReplicas}/{.status.replicas} replicas listas (ClusterIP, sin NodePort)' || echo "Postgres: no encontrado"
	@echo ""
	@echo "---"
	@echo "API:        minikube service api-external -n $(NAMESPACE)       (NodePort 30081)"
	@echo "MQTT:       minikube service mosquitto-external -n $(NAMESPACE) (NodePort 31883)"
	@echo "Prometheus: minikube service prometheus-external -n $(NAMESPACE) (NodePort 30090)"
	@echo "Grafana:    minikube service grafana-external -n $(NAMESPACE)   (NodePort 30300)"
	@echo "Landing:    minikube service landing-external -n $(NAMESPACE)   (NodePort 30080)"

.PHONY: mk-all
mk-all: mk-start mk-build mk-load mk-apply mk-wait mk-status ## TODO en Minikube de una vez

.PHONY: hackathon-demo
hackathon-demo: ## Demo de mañana: cluster + stack + checklist pre-demo
	minikube start --driver=$(MINIKUBE_DRIVER) --cpus=2 --memory=4096 || true
	$(MAKE) mk-apply
	kubectl wait --for=condition=available deployment/api deployment/grafana deployment/landing deployment/mosquitto deployment/prometheus -n $(NAMESPACE) --timeout=300s
	@$(MAKE) mk-status
	@echo "--- checklist pre-demo (lección 8) ---"
	@echo "1. curl localhost:8001/health -> roboflow.configured: true (si false: falta key)"
	@echo "2. Consola Qt: make cam-consola (dropdown: Streamplify, Re-scan si se reconectó)"
	@echo "3. Fotos impresas en mate a 20-30 cm (no pantalla: moiré)"
	@echo "4. Landing: minikube service landing-external -n $(NAMESPACE)"
	@echo "5. Grafana: minikube service grafana-external -n $(NAMESPACE)"
	@echo "(inference self-hosted: ver deployment/inference aparte; pull pesado la víspera)"

.PHONY: mk-clean
mk-clean: ## Borra los recursos del namespace (no borra el cluster)
	kubectl delete -f $(K8S_DIR)/inference.yaml --ignore-not-found
	kubectl delete -f $(K8S_DIR)/landing.yaml --ignore-not-found
	kubectl delete -f $(K8S_DIR)/monitoring.yaml --ignore-not-found
	kubectl delete -f $(K8S_DIR)/agrivision.yaml --ignore-not-found

.PHONY: mk-image-backend
mk-image-backend: ## Construye y carga solo la imagen del backend
	docker build --load -t $(API_IMAGE) backend/
	minikube image load $(API_IMAGE)

.PHONY: mk-image-landing
mk-image-landing: ## Construye y carga solo la imagen del landing
	docker build --load -t $(LANDING_IMAGE) landing/
	minikube image load $(LANDING_IMAGE)

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
