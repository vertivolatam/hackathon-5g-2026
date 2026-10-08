"""Inserta datos demo en PostgreSQL (idempotente por id).

Uso:
  cd backend
  python scripts/seed.py

Requiere DATABASE_URL (por defecto postgresql+psycopg://agrivision:agrivision@localhost:5432/agrivision)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import SessionLocal, init_db, Cooperativa, Finca, Tecnico, Visita, Incidencia


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
    finally:
        db.close()


if __name__ == "__main__":
    seed()
