---
sidebar_position: 4
---

# Alertas por Telegram

El backend empuja foto + caption ante detecciones sobre el umbral (`backend/notify.py`, solo stdlib). Patrón del [tutorial de Telegram Bot](https://gitlab.com/Athamaxy/telegram-bot-tutorial/-/blob/main/TutorialBot.py) adaptado a push: sin polling ni comandos, solo `sendPhoto`/`sendMessage` por HTTPS.

## 1. Crear el bot y el destino (una vez)

1. Hablar con `@BotFather` → `/newbot` → anota el **token**.
2. Crear el canal/grupo de alertas, agregar el bot como admin, anotar el **chat_id** (con `@getmyid_bot` o `getUpdates`).

## 2. Cablear al backend

```bash
# El token entra por stash (nunca en claro): /secret-input, luego
# /secret-use TELEGRAM_BOT_TOKEN -- bash -c 'printf "TELEGRAM_BOT_TOKEN=%s\n" "$TELEGRAM_BOT_TOKEN" > .telegram.env'
# El chat ID (no es secreto) se agrega: TELEGRAM_CHAT_ID=-100... >> .telegram.env
# Ambos archivos 0600, gitignoreados; compose los lee por env_file (lecciones 8 y 14).
```

Sin ambas variables el backend es no-op (loguea nada, no falla): el resto sigue vivo. Tras editar `.py`: `make dev-restart` (uvicorn no recarga solo, lección 19).

```bash
# Minikube: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID en backend/k8s/agrivision.yaml
# (hoy van vacíos; para la demo en cluster, cablear vía SealedSecret como ROBOFLOW_API_KEY).
```

Sin ambas variables el backend es no-op (loguea nada, no falla): el resto sigue vivo.

## 3. Verificar

Subir una foto con broca ≥ `ALERT_MIN_CONF` a `POST /api/fotos` + `POST /api/detect`: el chat recibe la foto con trampa, modelo y confianzas. Métrica: `agrivision_telegram_total` (ver `/metrics`).
