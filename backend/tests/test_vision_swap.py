"""Intercambio del modelo de visión (broca -> cualquier plaga/enfermedad).

El backend es agnóstico al modelo: ROBOFLOW_MODEL_ID, ALERT_CLASSES y
ALERT_MIN_CONF salen de entorno, y el parse de predicciones usa
p.get("class") genérico. Estos tests lo demuestran con un rf_detect
falso que devuelve otra plaga (roya) y otro MODEL_ID, sin red.
"""

BODY = {"trap_id": "trap-09", "image_base64": "aGk="}


def _fake_roya(image_b64, timeout=60):
    assert image_b64 == "aGk="
    return {
        "model_id": "mi-ws/roya-cafe/3",
        "predictions": [
            {"class": "roya", "confidence": 0.91, "x": 1, "y": 2, "width": 3, "height": 4,
             "points": [{"x": 0, "y": 0}, {"x": 2, "y": 0}, {"x": 1, "y": 4}]},
            {"class": "hoja-sana", "confidence": 0.2, "x": 0, "y": 0, "width": 1, "height": 1},
        ],
    }


def test_detect_usa_otro_modelo_y_otra_clase(client, monkeypatch):
    import app as appmod

    monkeypatch.setattr(appmod, "rf_configured", lambda: True)
    monkeypatch.setattr(appmod, "rf_detect", _fake_roya)
    monkeypatch.setattr(appmod, "ALERT_CLASSES", {"roya"})
    monkeypatch.setattr(appmod, "ALERT_MIN_CONF", 0.5)
    llamadas = []
    monkeypatch.setattr(
        appmod.notify, "alert_if_needed",
        lambda *a, **k: llamadas.append((a, k)) or True,
    )
    r = client.post("/api/detect", json=BODY)
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["model"] == "mi-ws/roya-cafe/3"
    assert out["detections"][0]["class"] == "roya"
    assert out["detections"][0]["polygon"] == [[0.0, 0.0], [2.0, 0.0], [1.0, 4.0]]
    assert out["detections"][1]["polygon"] is None  # solo caja: sin máscara
    assert llamadas, "debió evaluar alerta para roya"
    assert llamadas[0][1]["classes"] == {"roya"}


def test_clase_fuera_de_alerta_no_dispara(client, monkeypatch):
    import app as appmod

    monkeypatch.setattr(appmod, "rf_configured", lambda: True)
    monkeypatch.setattr(appmod, "rf_detect", _fake_roya)
    monkeypatch.setattr(appmod, "ALERT_CLASSES", {"broca"})
    llamadas = []
    monkeypatch.setattr(
        appmod.notify, "alert_if_needed",
        lambda *a, **k: llamadas.append((a, k)) or False,
    )
    r = client.post("/api/detect", json=BODY)
    assert r.status_code == 201
    assert llamadas[0][1]["classes"] == {"broca"}  # roya no es broca: sin alerta


def test_umbral_filtra_baja_confianza(monkeypatch):
    import notify as notifymod

    monkeypatch.setattr(notifymod, "BOT_TOKEN", "tok")
    monkeypatch.setattr(notifymod, "CHAT_ID", "123")
    assert notifymod.alert_if_needed("t", "m", [{"class": "broca", "confidence": 0.1}],
                                     "eA==", classes={"broca"}, min_conf=0.5) is False


def test_caption_incluye_trampa_y_confianza():
    import notify as notifymod

    cap = notifymod.build_caption("trap-09", "mi-ws/roya-cafe/3",
                                  [{"class": "roya", "confidence": 0.91}], 0.5)
    assert "trap-09" in cap and "91%" in cap and "roya" in cap


def test_sin_token_no_hace_nada(monkeypatch):
    import notify as notifymod

    monkeypatch.setattr(notifymod, "BOT_TOKEN", "")
    monkeypatch.setattr(notifymod, "CHAT_ID", "")
    assert notifymod.configured() is False
    assert notifymod.alert_if_needed("t", "m", [{"class": "broca", "confidence": 0.9}],
                                     "eA==") is False
    assert notifymod.send_message("hola") is False


WORKFLOW_RESP = {
    "outputs": [{
        "annotated_image": {"type": "base64", "value": "iVBORw0="},
        "sam_3_predictions": {
            "image": {"width": 768, "height": 480},
            "predictions": [{
                "class": "broca-cafe", "x": 253.5, "width": 95, "height": 80,
                "y": 100.0,
                "points": [{"x": 240, "y": 80}, {"x": 270, "y": 85}, {"x": 255, "y": 120}],
            }],
        },
    }],
}


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        import json as _json
        return _json.dumps(self._payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_workflow_broca_cafe_con_poligono(client, monkeypatch):
    import app as appmod
    import vision as visionmod

    monkeypatch.setattr(visionmod, "ROBOFLOW_API_KEY", "k")
    monkeypatch.setattr(visionmod, "ROBOFLOW_WORKFLOW_ID",
                        "vertivo-una-huerta-pensada-para-vos/agrivision-demo-hackathon-5g-2026")
    monkeypatch.setattr(visionmod.urllib.request, "urlopen",
                        lambda req, timeout=60: _FakeResp(WORKFLOW_RESP))
    monkeypatch.setattr(appmod, "ALERT_CLASSES", {"broca", "broca-cafe"})
    llamadas = []
    monkeypatch.setattr(
        appmod.notify, "alert_if_needed",
        lambda *a, **k: llamadas.append((a, k)) or True,
    )
    r = client.post("/api/detect", json={
        "trap_id": "trap-01", "image_base64": "aGk=",
        "cliente": "demo", "finca": "norte"})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["model"] == ("vertivo-una-huerta-pensada-para-vos/"
                            "agrivision-demo-hackathon-5g-2026")
    det = out["detections"][0]
    assert det["class"] == "broca-cafe"
    assert det["confidence"] == 1.0  # SAM no da confianza: se asume 1.0
    assert det["polygon"] == [[240.0, 80.0], [270.0, 85.0], [255.0, 120.0]]
    assert llamadas, "broca-cafe debió evaluar alerta"
