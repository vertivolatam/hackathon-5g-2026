"""Cliente liviano (solo stdlib) para inferencia RF-DETR de Roboflow.

Dos rutas, mismo código (solo cambia ROBOFLOW_URL):
  1. Serverless Cloud API (default): https://serverless.roboflow.com
     GPU auto-escalable de Roboflow, cobra créditos por imagen.
  2. Self-hosted Inference Server: http://localhost:9001
     (`pip install inference-cli && inference server start`).
     Sin créditos; tú pones el hardware.

Flujo previo (una sola vez, en app.roboflow.com):
  Fork del dataset coffee-berry-borer de Universe -> Train RF-DETR
  (notebook o Roboflow Train) -> Deploy -> MODEL_ID `workspace/project/1`.

Nota: los endpoints legacy detect.roboflow.com están deprecados;
se usa serverless con `Authorization: Bearer` (nunca api_key en URL).
"""
import base64
import json
import os
import urllib.parse
import urllib.request
import uuid

ROBOFLOW_URL = os.getenv("ROBOFLOW_URL", "https://serverless.roboflow.com")
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "")  # ej: tu-ws/coffee-berry-borer/1
ROBOFLOW_WORKFLOW_ID = os.getenv("ROBOFLOW_WORKFLOW_ID", "")  # ej: tu-ws/mi-workflow (Workflow SAM prompting: prioridad sobre MODEL_ID)
ROBOFLOW_CONFIDENCE = float(os.getenv("ROBOFLOW_CONFIDENCE", "0.4"))


def configured() -> bool:
    return bool(ROBOFLOW_API_KEY and (ROBOFLOW_MODEL_ID or ROBOFLOW_WORKFLOW_ID))


def _multipart(image_bytes: bytes) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    head = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
        f'filename="image.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + image_bytes + tail, boundary


def detect_b64(image_b64: str, timeout: int = 60) -> dict:
    """Envía una imagen (base64) al modelo y devuelve predicciones.

    Dos modos (ver ROBOFLOW_WORKFLOW_ID): Workflow (SAM prompting,
    ej. agrivision-demo con broca-cafe + polígonos) o modelo directo
    (RF-DETR entrenado). Devuelve {"model_id", "predictions"} en ambos.
    """
    if not configured():
        raise RuntimeError(
            "Roboflow no configurado: define ROBOFLOW_API_KEY y "
            "ROBOFLOW_WORKFLOW_ID o ROBOFLOW_MODEL_ID"
        )
    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception:
        raise ValueError("image_base64 no es base64 válido")
    if len(image_bytes) > 20 * 1024 * 1024:
        raise ValueError("imagen > 20MB (límite serverless)")
    if ROBOFLOW_WORKFLOW_ID:
        return _detect_workflow(image_b64, timeout)
    return _detect_model(image_bytes, timeout)


def _post_json(url: str, payload: dict, timeout: int) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ROBOFLOW_API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Roboflow HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Roboflow inalcanzable: {e.reason}")


def _detect_workflow(image_b64: str, timeout: int) -> dict:
    """Ejecuta un Workflow (SAM prompting) y normaliza su salida.

    Endpoint: POST {URL}/infer/workflows/{workspace}/{workflow} con la
    imagen en base64. Las predicciones SAM no traen confidence: se
    asume 1.0 (el prompt ya es la decisión) para que los umbrales
    y alertas operen igual que con un modelo entrenado.
    """
    url = f"{ROBOFLOW_URL.rstrip('/')}/infer/workflows/{ROBOFLOW_WORKFLOW_ID.strip('/')}"
    data = _post_json(url, {
        "api_key": ROBOFLOW_API_KEY,
        "inputs": {"image": {"type": "base64", "value": image_b64}},
    }, timeout)
    preds = _extract_workflow_predictions(data)
    for p in preds:
        p.setdefault("confidence", 1.0)
    return {"model_id": ROBOFLOW_WORKFLOW_ID, "predictions": preds}


def _extract_workflow_predictions(data: dict) -> list:
    """Saca la lista de predicciones de cualquier forma de outputs."""
    outputs = data.get("outputs") or []
    if isinstance(outputs, dict):
        outputs = [outputs]
    for out in outputs:
        if not isinstance(out, dict):
            continue
        for key, val in out.items():
            if "predict" not in key.lower():
                continue
            if isinstance(val, list):
                return val
            if isinstance(val, dict) and isinstance(val.get("predictions"), list):
                return val["predictions"]
    if isinstance(data.get("predictions"), list):
        return data["predictions"]
    return []


def _detect_model(image_bytes: bytes, timeout: int) -> dict:
    params = urllib.parse.urlencode({"confidence": ROBOFLOW_CONFIDENCE})
    url = f"{ROBOFLOW_URL.rstrip('/')}/{ROBOFLOW_MODEL_ID.strip('/')}?{params}"
    body, boundary = _multipart(image_bytes)
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {ROBOFLOW_API_KEY}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Roboflow HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Roboflow inalcanzable: {e.reason}")
