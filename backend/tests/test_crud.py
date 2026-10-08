def test_crud_tecnico(client, auth_headers):
    r = client.post(
        "/api/tecnicos",
        json={"id": "t1", "cooperativaId": "coop-1", "nombre": "Juan", "correo": "j@t.cr", "especialidad": "Riego"},
        headers=auth_headers,
    )
    assert r.status_code == 201

    r = client.get("/api/tecnicos?cooperativaId=coop-1", headers=auth_headers)
    assert any(t["id"] == "t1" for t in r.json()["items"])

    r = client.put("/api/tecnicos/t1", json={"especialidad": "Fitosanidad"}, headers=auth_headers)
    assert r.json()["especialidad"] == "Fitosanidad"

    r = client.delete("/api/tecnicos/t1", headers=auth_headers)
    assert r.status_code == 204


def test_crud_incidencia(client, auth_headers):
    r = client.post(
        "/api/incidencias",
        json={"id": "i-test", "tipo": "Roya", "severidad": 30, "nivelRiesgo": "Media", "lat": 9.9, "lng": -84.1, "fecha": "2026-10-01", "finca": "F"},
        headers=auth_headers,
    )
    assert r.status_code == 201

    r = client.get("/api/incidencias", headers=auth_headers)
    assert any(i["id"] == "i-test" for i in r.json()["items"])

    r = client.put("/api/incidencias/i-test", json={"severidad": 45}, headers=auth_headers)
    assert r.json()["severidad"] == 45

    r = client.delete("/api/incidencias/i-test", headers=auth_headers)
    assert r.status_code == 204


def test_get_recurso_sin_token_retorna_401(client):
    r = client.get("/api/fincas")
    assert r.status_code == 401
    r = client.post("/api/cooperativas", json={"id": "x", "nombre": "x"})
    assert r.status_code == 401


def test_actualizar_recurso_inexistente(client, auth_headers):
    r = client.put("/api/fincas/no-existe", json={"nombre": "x"}, headers=auth_headers)
    assert r.status_code == 404


def test_eliminar_recurso_inexistente(client, auth_headers):
    r = client.delete("/api/visitas/no-existe", headers=auth_headers)
    assert r.status_code == 404
