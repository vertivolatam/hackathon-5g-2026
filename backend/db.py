"""Persistencia PostgreSQL: modelos y sesión (reemplaza los deque en memoria)."""
import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float, Boolean, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://agrivision:agrivision@localhost:5432/agrivision")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class TelemetryItem(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    payload = Column(JSON)
    raw = Column(String, nullable=True)
    ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    trap_id = Column(String, index=True)
    model = Column(String, default="")
    detections = Column(JSON)
    ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Foto(Base):
    """Foto de trampa (binario en bytea + metadatos).

    El binario vive en Postgres para que Grafana lo lea directo con
    ``encode(data, 'base64')`` en el panel Business Media
    (volkovlabs-image-panel). Vale para demo y piloto; a escala de
    1.000 trampas migrar el binario a object storage (S3) dejando aquí
    solo metadatos + URL (ver docs reference/fotos-pipeline).
    """

    __tablename__ = "fotos"

    id = Column(Integer, primary_key=True, index=True)
    trap_id = Column(String, index=True)
    filename = Column(String, default="")
    content_type = Column(String, default="image/jpeg")
    size_bytes = Column(Integer, default=0)
    data = Column(LargeBinary)
    ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Cooperativa(Base):
    __tablename__ = "cooperativas"

    id = Column(String, primary_key=True)
    nombre = Column(String)
    region = Column(String)
    correo = Column(String)
    logo = Column(String, default="")
    activa = Column(Boolean, default=True)


class Finca(Base):
    __tablename__ = "fincas"

    id = Column(String, primary_key=True)
    cooperativaId = Column(String, index=True)
    nombre = Column(String)
    propietario = Column(String)
    area = Column(Float, default=0)
    descripcion = Column(String, default="")
    poligono = Column(JSON, default=list)
    sensores = Column(JSON, default=list)
    riesgo = Column(String, default="Bajo")
    ultimaAlerta = Column(String, default="—")
    visitasPendientes = Column(Integer, default=0)
    prioridad = Column(String, default="Sin prioridad inmediata")
    lecturaActual = Column(JSON, nullable=True)
    detecciones = Column(JSON, default=list)
    tendenciaSeveridad = Column(JSON, default=list)
    actividadSensores = Column(JSON, default=list)


class Tecnico(Base):
    __tablename__ = "tecnicos"

    id = Column(String, primary_key=True)
    cooperativaId = Column(String, index=True)
    nombre = Column(String)
    correo = Column(String, index=True)
    telefono = Column(String, default="")
    especialidad = Column(String, default="")
    disponible = Column(Boolean, default=True)
    activo = Column(Boolean, default=True)


class Visita(Base):
    __tablename__ = "visitas"

    id = Column(String, primary_key=True)
    cooperativaId = Column(String, index=True)
    fincaId = Column(String)
    tecnicoId = Column(String)
    fincaNombre = Column(String, default="")
    tecnicoNombre = Column(String, default="")
    tecnicoCorreo = Column(String, default="")
    propietarioCorreo = Column(String, default="")
    fecha = Column(String, default="")
    hora = Column(String, default="")
    motivo = Column(String, default="")
    estado = Column(String, default="Pendiente")
    observaciones = Column(String, default="")
    resultado = Column(String, default="")
    recordatorioManualPendiente = Column(Boolean, default=False)


class Incidencia(Base):
    __tablename__ = "incidencias"

    id = Column(String, primary_key=True)
    tipo = Column(String)
    severidad = Column(Integer, default=0)
    nivelRiesgo = Column(String, default="Baja")
    lat = Column(Float, default=0)
    lng = Column(Float, default=0)
    fecha = Column(String, default="")
    finca = Column(String, default="")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    rol = Column(String)  # administrador | cooperativa | tecnico
    cooperativaId = Column(String, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)
    _enable_timescale()


def _enable_timescale():
    """Convierte telemetry/detections en hypertables si hay TimescaleDB.

    Timescale es solo Postgres: los modelos SQLAlchemy mapean igual sobre
    una hypertable que sobre una tabla normal. Best-effort: en Postgres
    pelado (dev sin extensión) falla el CREATE EXTENSION y se sigue con
    tablas normales.
    """
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            for tabla in ("telemetry", "detections"):
                conn.execute(
                    text(
                        "SELECT create_hypertable('%s', 'ts', "
                        "if_not_exists => TRUE);" % tabla
                    )
                )
            conn.commit()
    except Exception:
        pass
