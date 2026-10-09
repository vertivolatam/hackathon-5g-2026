"""La alerta lleva la foto anotada (polígonos + tags), no el crudo."""

import base64
import io

from PIL import Image

from annotate import annotate_detections


def _jpeg(w=640, h=480):
    img = Image.new("RGB", (w, h), (200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_anota_poligono_y_cambia_bytes():
    raw = _jpeg()
    preds = [{"class": "broca-cafe", "confidence": 0.81,
              "bbox": {}, "polygon": [[10, 10], [100, 10], [100, 100], [10, 100]]}]
    out = annotate_detections(raw, preds, 0.5)
    assert out != raw  # hay trazo + tag + barra de veredicto
    Image.open(io.BytesIO(out)).verify()


def test_sin_detecciones_no_lanza():
    out = annotate_detections(_jpeg(), [], 0.5)
    Image.open(io.BytesIO(out)).verify()


def test_b64_redondo():
    raw = _jpeg()
    preds = [{"class": "broca-cafe", "confidence": 0.9,
              "bbox": {"x": 320, "y": 240, "width": 60, "height": 60},
              "polygon": None}]
    rt = base64.b64decode(base64.b64encode(
        annotate_detections(raw, preds, 0.5)).decode())
    Image.open(io.BytesIO(rt)).verify()
