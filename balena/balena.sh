#!/usr/bin/env bash
# Flasheo gateway Raspberry Pi 4 64-bit por balenaCLI (v25, docs.balena.io/reference/balena-cli/latest).
# El link efp.balena.io/open-image-url no auto-abrió Etcher en tu sesión: este es el camino CLI equivalente.
# Secretos (WIFI_KEY, BALENA_TOKEN) por entorno, nunca en git.
set -euo pipefail

: "${FLEET:?export FLEET=org/fleet}"
: "${WIFI_SSID:=NOKIA-C80A}"
: "${WIFI_KEY:?export WIFI_KEY=...}"
: "${BALENA_TOKEN:?export BALENA_TOKEN=... # balena login --token o api-key generate}"
VERSION="${VERSION:-8.0.9+rev2}"
DEVICE_TYPE="${DEVICE_TYPE:-raspberrypi4-64}"
DRIVE="${DRIVE:-}"  # ej. /dev/sda (tu SD 29.1G). Verificar con `balena util available-drives`.

export BALENARC_NO_PROXY='*.local,192.168.*'
balena login --token "$BALENA_TOKEN"
balena device-type list | grep -F "$DEVICE_TYPE"
balena util available-drives

IMG="$(mktemp -d)/balena.img"
balena os download "$DEVICE_TYPE" --version "$VERSION" --output "$IMG"
balena config generate --fleet "$FLEET" --version "$VERSION" \
  --network wifi --wifiSsid "$WIFI_SSID" --wifiKey "$WIFI_KEY" \
  --appUpdatePollInterval 10 --output config.json
balena os configure "$IMG" --fleet "$FLEET" --config config.json

if [ -n "$DRIVE" ]; then
  # Equivalente a Etcher, destructivo: confirma que $DRIVE es la SD.
  balena os initialize "$IMG" --drive "$DRIVE" --yes
  # Alternativa todo-en-uno: balena device init --fleet "$FLEET" --os-version "$VERSION" --drive "$DRIVE"
else
  echo "IMG lista en $IMG (pasa DRIVE=/dev/sdX para escribir)"
fi
