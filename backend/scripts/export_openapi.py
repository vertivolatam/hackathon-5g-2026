"""Exporta el OpenAPI del backend a stdout.

Uso (desde la raíz del repo):
    python3 backend/scripts/export_openapi.py > /tmp/openapi.json

Requiere las deps de backend/requirements.txt (fastapi, paho-mqtt).
El CI lo ejecuta con las versiones pineadas; en local puede variar.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app  # noqa: E402

print(json.dumps(app.openapi(), indent=2, ensure_ascii=False))
