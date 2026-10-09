"""POST /api/eventos: watchdog de cámara (tirón de cable) -> Telegram."""

import notify as notifymod


def test_caption_camara_perdida():
    cap = notifymod.evento_caption("camara-perdida", "trap-edge", "La Haya", "read falló x15")
    assert "trap-edge" in cap and "La Haya" in cap
    assert "MIPI" in cap and "read falló x15" in cap


def test_caption_camara_recuperada():
    cap = notifymod.evento_caption("camara-recuperada", "trap-edge")
    assert "trap-edge" in cap and "línea" in cap


def test_evento_sin_config_es_noop(monkeypatch):
    monkeypatch.setattr(notifymod, "BOT_TOKEN", "")
    monkeypatch.setattr(notifymod, "CHAT_ID", "")
    assert notifymod.alert_evento("t", "camara-perdida") is False


def test_evento_empuja_mensaje(monkeypatch):
    monkeypatch.setattr(notifymod, "BOT_TOKEN", "tok")
    monkeypatch.setattr(notifymod, "CHAT_ID", "123")
    enviados = []
    monkeypatch.setattr(notifymod, "send_message", lambda text: enviados.append(text) or True)
    assert notifymod.alert_evento("trap-edge", "camara-perdida", "La Haya", "x") is True
    import time

    for _ in range(100):
        if enviados:
            break
        time.sleep(0.05)
    assert enviados and "trap-edge" in enviados[0]
