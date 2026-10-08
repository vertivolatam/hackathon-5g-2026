# edge-gateway/balena-provisioning

Gateway de finca (Raspberry Pi 4 64-bit) provisionado con balenaOS de forma repetible y auditable, sin depender del link Etcher del dashboard.

## ADDED Requirements

### Requirement: Flujo de flasheo por balenaCLI versionado

El repo SHALL proveer un script que ejecute, en orden, `login --token`, `device-type list`, `util available-drives`, `os download`, `config generate`, `os configure` y `os initialize` (o `device init` como alternativa todo-en-uno), fijando `raspberrypi4-64`, balenaOS `8.0.9+rev2`, red wifi, SSID y `appUpdatePollInterval=10`.

#### Scenario: Provisionamiento documentado

- WHEN un operador sigue `balena/balena.sh` con `FLEET`, `WIFI_SSID`, `WIFI_KEY` y `BALENA_TOKEN` en entorno
- THEN obtiene una SD que arranca balenaOS en modo desarrollo conectada al fleet indicado.

### Requirement: Cero secretos en el repositorio

Ni claves wifi ni tokens SHALL existir en archivos versionados. Todo secreto SHALL entrar por variables de entorno.

#### Scenario: Auditoría de secretos

- WHEN se busca `wifiKey`, `wifi_key`, `Bearer` o `gho_` en el repo
- THEN no SHALL haber coincidencias fuera de placeholders.

### Requirement: Composición gateway + provisionador ESP32

El repo SHALL declarar en `docker-compose.yml` el servicio `gateway` (Raspberry Pi 4) y el servicio `esp-provisioner` (flasheo del leaf ESP32-P4 por USB/UART vía `espflash`), con volúmenes para el firmware compilado.

#### Scenario: Despliegue del fleet

- WHEN se hace `balena deploy`/`balena push` del directorio `balena/`
- THEN ambos servicios SHALL definirse y el provisionador SHALL tener acceso al puerto serie del leaf.

### Requirement: Uplink 5G con RM520N-GL

El gateway SHALL usar el HAT RM520N-GL por USB 3.0 en modo MBIM (`AT+QCFG="usbnet",2`), con alimentación externa 5V/3A al HAT y APN del core privado configurado en el host por AT (`AT+CGDCONT`), nunca en git. El `agent.py` SHALL parametrizarse solo por entorno (`MQTT_HOST`, `BACKEND_URL`, `TRAP_ID`, `INTERVAL_S`, `ALERT_*`) y SHALL correr como CMD del servicio `gateway`.

#### Scenario: Gateway con 5G activo

- WHEN el HAT registra en el PLMN privado (`AT+C5GREG?` con estado registrado) y `agent.py` arranca
- THEN la telemetría SHALL llegar a `agrivision/telemetry` y las fotos a `POST /api/detect` sin cambios en el agent.
