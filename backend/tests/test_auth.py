from auth import hash_password, verificar_password, crear_token, usuario_actual, JWT_EXP_MIN
import jwt
import time


def test_hash_and_verify_password():
    h = hash_password("secreto123")
    assert h != "secreto123"
    assert verificar_password("secreto123", h)
    assert not verificar_password("otra", h)


def test_login_ok_y_token_valido(client):
    r = client.post("/api/auth/login", json={"email": "admin@bioagro.cr", "password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert data["rol"] == "administrador"
    payload = jwt.decode(data["token"], "test-secret", algorithms=["HS256"])
    assert payload["sub"] == "admin@bioagro.cr"


def test_login_password_incorrecto(client):
    r = client.post("/api/auth/login", json={"email": "admin@bioagro.cr", "password": "mal"})
    assert r.status_code == 401


def test_endpoint_protegido_sin_token(client):
    r = client.get("/api/cooperativas")
    assert r.status_code == 401


def test_crud_cooperativa(client, auth_headers):
    # crear
    r = client.post(
        "/api/cooperativas",
        json={"id": "c-test", "nombre": "Coop Test", "region": "Norte", "correo": "t@t.cr", "activa": True},
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["id"] == "c-test"

    # listar
    r = client.get("/api/cooperativas", headers=auth_headers)
    assert r.status_code == 200
    assert any(c["id"] == "c-test" for c in r.json()["items"])

    # actualizar
    r = client.put("/api/cooperativas/c-test", json={"nombre": "Coop Test 2"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["nombre"] == "Coop Test 2"

    # eliminar
    r = client.delete("/api/cooperativas/c-test", headers=auth_headers)
    assert r.status_code == 204

    r = client.get("/api/cooperativas", headers=auth_headers)
    assert not any(c["id"] == "c-test" for c in r.json()["items"])


def test_crud_finca_y_visita(client, auth_headers):
    client.post("/api/fincas", json={"id": "f-test", "cooperativaId": "coop-1", "nombre": "Finca Test", "propietario": "P", "area": 5}, headers=auth_headers)
    r = client.get("/api/fincas?cooperativaId=coop-1", headers=auth_headers)
    assert any(f["id"] == "f-test" for f in r.json()["items"])

    client.post("/api/visitas", json={"id": "v-test", "cooperativaId": "coop-1", "fincaId": "f-test", "tecnicoId": "t-1", "fecha": "2026-10-10", "hora": "09:00", "motivo": "Revisión"}, headers=auth_headers)
    r = client.put("/api/visitas/v-test", json={"estado": "Completada"}, headers=auth_headers)
    assert r.json()["estado"] == "Completada"
