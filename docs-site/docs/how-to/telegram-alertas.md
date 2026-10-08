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
# compose dev (ver docker-compose.dev.yml)
TELEGRAM_BOT_TOKEN=123456:ABC... TELEGRAM_CHAT_ID=-100... docker compose up -d backend
# Minikube: env TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID en backend/k8s/agrivision.yaml
```

Sin ambas variables el backend es no-op (loguea nada, no falla): el resto sigue vivo.

## 3. Verificar

Subir una foto con broca ≥ `ALERT_MIN_CONF` a `POST /api/fotos` + `POST /api/detect`: el chat recibe la foto con trampa, modelo y confianzas. Métrica: `agrivision_telegram_total` (ver `/metrics`).
