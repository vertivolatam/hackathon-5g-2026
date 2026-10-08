import pytest

PNG_1PX = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture()
def trap_key(client, monkeypatch):
    monkeypatch.setenv("FOTO_API_KEY", "clave-trampa-test")
    import app as appmod

    monkeypatch.setattr(appmod, "FOTO_API_KEY", "clave-trampa-test")
    return {"X-Trap-Key": "clave-trampa-test"}


def _subir(client, headers, data=PNG_1PX, trap="trap-01", filename="t1.jpg"):
    return client.post(
        "/api/fotos",
        files={"file": (filename, data, "image/jpeg")},
        data={"trap_id": trap},
        headers=headers,
    )


def test_subir_foto_ok_y_lecturas(client, trap_key):
    r = _subir(client, trap_key)
    assert r.status_code == 201, r.text
    meta = r.json()
    assert meta["trap_id"] == "trap-01" and meta["size_bytes"] == len(PNG_1PX)

    r = client.get("/api/fotos?trap_id=trap-01")
    assert r.status_code == 200 and r.json()["count"] >= 1

    r = client.get(f"/api/fotos/{meta['id']}")
    assert r.status_code == 200 and r.content == PNG_1PX
    assert r.headers["content-type"] == "image/jpeg"

    r = client.get("/api/fotos/latest?trap_id=trap-01")
    assert r.status_code == 200 and r.content == PNG_1PX


def test_subir_sin_key_retorna_401(client, monkeypatch):
    import app as appmod

    monkeypatch.setattr(appmod, "FOTO_API_KEY", "exigida")
    r = _subir(client, {})
    assert r.status_code == 401


def test_subir_no_imagen_retorna_415(client, trap_key):
    r = client.post(
        "/api/fotos",
        files={"file": ("t.txt", b"hola", "text/plain")},
        data={"trap_id": "trap-01"},
        headers=trap_key,
    )
    assert r.status_code == 415


def test_latest_sin_fotos_retorna_404(client):
    r = client.get("/api/fotos/latest?trap_id=trap-sin-fotos")
    assert r.status_code == 404
    r = client.get("/api/fotos/999999")
    assert r.status_code == 404


def test_metricas_fotos(client, trap_key):
    _subir(client, trap_key, trap="trap-metrics")
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    assert "agrivision_fotos_total" in body
