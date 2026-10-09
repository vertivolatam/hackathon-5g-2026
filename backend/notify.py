"""Alertas por Telegram Bot API (solo stdlib, sin dependencias nuevas).

Patrón tomado de
https://gitlab.com/Athamaxy/telegram-bot-tutorial/-/blob/main/TutorialBot.py
(token + chat_id + parse HTML), pero invertido: el tutorial implementa un
bot interactivo (polling + comandos + echo) y aquí el backend actúa solo
como EMISOR push (sendMessage/sendPhoto) ante detecciones de broca.
Sin polling, sin Updater, sin hilos propios: un thread daemon por alerta.

Config por entorno: TELEGRAM_BOT_TOKEN (de @BotFather), TELEGRAM_CHAT_ID
(chat o canal destino). Sin ambos, todo es no-op (dev sin Telegram).
"""

import json
import os
import threading
import urllib.parse
import urllib.request

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
API = "https://api.telegram.org/bot%s/%s"


def configured() -> bool:
    """True si hay destino de alertas configurado."""
    return bool(BOT_TOKEN and CHAT_ID)


def build_caption(trap_id, model, preds, min_conf, finca="") -> str:
    """Texto HTML legible: finca (NDD/sector 5G) + trampa + conteo.

    Sin slug del modelo ni líneas por clase: el detalle visual va en la
    foto anotada que acompaña al mensaje.
    """
    top = [p for p in (preds or []) if (p.get("confidence") or 0) >= min_conf]
    mx = max([(p.get("confidence") or 0) for p in top] + [0])
    donde = ("<code>%s</code> · trampa <code>%s</code>" % (finca, trap_id)
             if finca and finca != "demo" else "trampa <code>%s</code>" % trap_id)
    return (
        "🚨 <b>Broca detectada</b> en %s\n"
        "%d broca(s), máx %.0f%% (umbral %.0f%%)"
        % (donde, len(top), 100 * mx, 100 * min_conf)
    )


def _post(method, fields, files=None):
    """POST a la Bot API. Devuelve True si Telegram respondió ok."""
    if not configured():
        return False
    if files:
        boundary = "agri%s" % os.getpid()
        body = b""
        for k, v in fields.items():
            body += (
                "--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                % (boundary, k, v)
            ).encode()
        for k, (fname, ctype, data) in files.items():
            body += (
                "--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
                "Content-Type: %s\r\n\r\n" % (boundary, k, fname, ctype)
            ).encode() + data + b"\r\n"
        body += ("--%s--\r\n" % boundary).encode()
        req = urllib.request.Request(
            API % (BOT_TOKEN, method),
            data=body,
            headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary},
            method="POST",
        )
    else:
        req = urllib.request.Request(
            API % (BOT_TOKEN, method),
            data=urllib.parse.urlencode(fields).encode(),
            method="POST",
        )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8")).get("ok", False)
    except Exception:
        return False


def send_message(text) -> bool:
    """Envía texto con formato HTML al chat configurado."""
    return _post("sendMessage", {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})


def send_photo(jpeg_bytes, caption) -> bool:
    """Envía la foto de la trampa con su caption de alerta."""
    return _post(
        "sendPhoto",
        {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
        files={"photo": ("trampa.jpg", "image/jpeg", jpeg_bytes)},
    )


def alert_if_needed(trap_id, model, preds, image_b64, classes=("broca",), min_conf=0.5,
                    finca=""):
    """Dispara la alerta en background si hay clase prioritaria ≥ umbral.

    Nunca lanza ni bloquea: sin config es no-op; con config, un thread
    daemon envía foto + caption sin frenar la respuesta HTTP.
    """
    if not configured():
        return False
    hit = any(
        (p.get("class") in classes) and ((p.get("confidence") or 0) >= min_conf)
        for p in (preds or [])
    )
    if not hit:
        return False
    caption = build_caption(trap_id, model, preds, min_conf, finca=finca)

    def _send():
        try:
            image_bytes = __import__("base64").b64decode(image_b64)
        except Exception:
            image_bytes = b""
        if image_bytes:
            send_photo(image_bytes, caption)
        else:
            send_message(caption)

    threading.Thread(target=_send, daemon=True).start()
    return True


def evento_caption(tipo, trap_id, finca="", detalle="") -> str:
    """Caption humano para eventos de trampa (sin foto: no hay cámara).

    `camara-perdida` es la cereza demo: simula el corte del MIPI CSI-2/USB
    en campo (o el tirón accidental del cable en la demo).
    """
    donde = ("<code>%s</code> · trampa <code>%s</code>" % (finca, trap_id)
             if finca and finca != "demo" else "trampa <code>%s</code>" % trap_id)
    if tipo == "camara-perdida":
        extra = ("\nÚltima señal: %s" % detalle) if detalle else ""
        return ("⚠️ Sin cámara en %s\n"
                "Posible corte del enlace (MIPI CSI-2 / USB) en campo.%s"
                % (donde, extra))
    if tipo == "camara-recuperada":
        return "✅ Cámara de %s de vuelta en línea." % donde
    if tipo == "health-ping":
        return ("💓 Trampa <code>%s</code> en línea\n%s"
                % (trap_id, detalle or "health ok"))
    return "ℹ️ Evento <code>%s</code> en %s%s" % (
        tipo, donde, ("\n%s" % detalle) if detalle else "")


def alert_evento(trap_id, tipo, finca="", detalle="") -> bool:
    """Push de evento sin foto, en background. Nunca lanza ni bloquea."""
    if not configured():
        return False
    caption = evento_caption(tipo, trap_id, finca, detalle)

    def _send():
        send_message(caption)

    threading.Thread(target=_send, daemon=True).start()
    return True


def announce_startup(roboflow_ok: bool) -> bool:
    """Prueba de vida al arrancar: el /health resumido en el grupo."""
    if not configured():
        return False
    caption = ("🟢 AgriVision backend en línea\n"
               "• Roboflow: <code>%s</code>\n"
               "• Alertas: este chat"
               % ("configurado" if roboflow_ok else "SIN KEY (solo fotos, sin detect)"))

    def _send():
        send_message(caption)

    threading.Thread(target=_send, daemon=True).start()
    return True
