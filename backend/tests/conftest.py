import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from db import SessionLocal, Usuario, init_db
from auth import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    try:
        if not db.query(Usuario).filter_by(email="admin@bioagro.cr").first():
            db.add(
                Usuario(
                    id="u1",
                    email="admin@bioagro.cr",
                    password_hash=hash_password("admin123"),
                    rol="administrador",
                )
            )
            db.commit()
    finally:
        db.close()
    yield


@pytest.fixture()
def client():
    from app import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def token(client):
    r = client.post("/api/auth/login", json={"email": "admin@bioagro.cr", "password": "admin123"})
    assert r.status_code == 200
    return r.json()["token"]


@pytest.fixture()
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
