"""Inserta datos demo en PostgreSQL (idempotente por id).

Uso:
  cd backend
  python scripts/seed.py

Requiere DATABASE_URL (por defecto postgresql+psycopg://agrivision:agrivision@localhost:5432/agrivision)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import SessionLocal, init_db, Cooperativa, Finca, Tecnico, Visita, Incidencia, TelemetryItem, Detection, Usuario
from auth import hash_password


def seed():
    init_db()
    db = SessionLocal()
    try:
        def upsert(modelo, id_, datos):
            obj = db.get(modelo, id_)
            if obj:
                return obj
            obj = modelo(id=id_, **datos)
            db.add(obj)
            return obj

        upsert(Cooperativa, "coop-1", {
            "nombre": "Cooperativa San José",
            "region": "Valle Central",
            "correo": "contacto@coopsj.cr",
            "logo": "",
            "activa": True,
        })

        upsert(Finca, "finca-1", {
            "cooperativaId": "coop-1",
            "nombre": "Finca El Cafetal",
            "propietario": "Juan Pérez",
            "area": 12.5,
            "descripcion": "Cafetal en ladera con sistema de riego por goteo.",
            "poligono": [[9.9281, -84.0907], [9.931, -84.088], [9.9335, -84.0915], [9.9305, -84.094]],
            "sensores": [
                {"id": "s1", "nombre": "Sensor humedad A", "lat": 9.9305, "lng": -84.0905, "activo": True},
                {"id": "s2", "nombre": "Sensor plaga B", "lat": 9.9318, "lng": -84.0912, "activo": False},
            ],
            "riesgo": "Medio",
            "ultimaAlerta": "2026-10-05 — Captura de broca 12% sobre umbral",
            "visitasPendientes": 1,
            "prioridad": "Alta",
            "lecturaActual": {
                "fecha": "2026-10-06 08:30",
                "temperatura": 24.5,
                "humedad": 78,
                "plagas": [{"tipo": "Broca", "severidad": 62}],
            },
            "detecciones": [
                {"fecha": "2026-10-05", "tipo": "Broca", "severidad": 62},
                {"fecha": "2026-10-03", "tipo": "Roya", "severidad": 28},
            ],
            "tendenciaSeveridad": [
                {"periodo": "Sep", "severidad": 55},
                {"periodo": "Oct", "severidad": 62},
            ],
            "actividadSensores": [
                {"periodo": "Sep", "activos": 1},
                {"periodo": "Oct", "activos": 1},
            ],
        })

        upsert(Tecnico, "tec-1", {
            "cooperativaId": "coop-1",
            "nombre": "María López",
            "correo": "tecnico@bioagro.cr",
            "telefono": "8888-0000",
            "especialidad": "Fitosanidad",
            "disponible": True,
            "activo": True,
        })

        upsert(Visita, "visita-1", {
            "cooperativaId": "coop-1",
            "fincaId": "finca-1",
            "tecnicoId": "tec-1",
            "fincaNombre": "Finca El Cafetal",
            "tecnicoNombre": "María López",
            "tecnicoCorreo": "tecnico@bioagro.cr",
            "propietarioCorreo": "juan.perez@example.com",
            "fecha": "2026-10-10",
            "hora": "09:00",
            "motivo": "Seguimiento de alerta",
            "estado": "Pendiente",
        })

        upsert(Usuario, "u-admin", {
            "email": "admin@bioagro.cr",
            "password_hash": hash_password("admin123"),
            "rol": "administrador",
            "cooperativaId": None,
        })
        upsert(Usuario, "u-coop", {
            "email": "coop@bioagro.cr",
            "password_hash": hash_password("coop123"),
            "rol": "cooperativa",
            "cooperativaId": "coop-1",
        })
        upsert(Usuario, "u-tecnico", {
            "email": "tecnico@bioagro.cr",
            "password_hash": hash_password("tecnico123"),
            "rol": "tecnico",
            "cooperativaId": "coop-1",
        })

        upsert(Incidencia, "i1", {
            "tipo": "Broca del café",
            "severidad": 85,
            "nivelRiesgo": "Alta",
            "lat": 9.9295,
            "lng": -84.0912,
            "fecha": "2026-10-06",
            "finca": "Finca La Palmera (ajena)",
        })

        db.commit()
        print("✅ Datos demo insertados (o ya existentes).")

        # Telemetría y detecciones demo (solo si las tablas están vacías)
        from datetime import datetime, timezone, timedelta

        if db.query(TelemetryItem).count() == 0:
            ahora = datetime.now(timezone.utc)
            for i in range(10):
                db.add(TelemetryItem(
                    topic="agrivision/trap-01",
                    payload={"temperatura": 24 + i * 0.3, "humedad": 70 + i, "broca": i % 3 == 0},
                    raw=None,
                    ts=ahora - timedelta(hours=i),
                ))
            db.commit()
            print("✅ Telemetría demo insertada.")

        if db.query(Detection).count() == 0:
            ahora = datetime.now(timezone.utc)
            for i in range(5):
                db.add(Detection(
                    trap_id="trap-01",
                    model="demo/coffee-berry-borer/1",
                    detections=[{"class": "broca", "confidence": 0.8, "bbox": {"x": 10, "y": 10, "width": 20, "height": 20}}],
                    ts=ahora - timedelta(hours=i * 2),
                ))
            db.commit()
            print("✅ Detecciones demo insertadas.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
