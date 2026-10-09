"""Simula una trampa ESP32-P4 contra el stack dev (sin hardware).

Publica telemetría MQTT (sensores + rssi + lux + cebo, como
apps/esp-32/main.py:read_sensors), sube una foto JPEG generada por
`POST /api/fotos` y prueba `POST /api/detect` (503 esperado sin keys
de Roboflow: valida el degradado limpio).

Uso:
    TRAP_ID=trap-sim MQTT_HOST=localhost API=http://localhost:8000 \\
    FOTO_API_KEY=dev-trap-key python3 scripts/sim_esp32.py [--fotos 3] [--tele 5]

Requiere: `make dev-full` (o backend+mosquitto+postgres) y paho-mqtt + Pillow.
"""

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

import paho.mqtt.publish as publish

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
API = os.getenv("API", "http://localhost:8000").rstrip("/")
TRAP_ID = os.getenv("TRAP_ID", "trap-sim")
TRAP_KEY = os.getenv("FOTO_API_KEY", "dev-trap-key")


def foto_jpeg(texto="BROCA-SIM"):
    """JPEG sintético 320x240 con texto (evita binarios en git)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (320, 240), (34, 139, 34))
    d = ImageDraw.Draw(img)
    d.rectangle([40, 60, 280, 180], outline=(255, 255, 255), width=3)
    d.text((60, 110), texto, fill=(255, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return buf.getvalue()


def _video_nodes():
    """Nodos /dev/video* ordenados (solo captura real, no metadata)."""
    import glob
    import os
    nodes = []
    for path in sorted(glob.glob("/dev/video*")):
        try:
            with open("/sys/class/video4linux/%s/name" % os.path.basename(path)) as f:
                name = f.read()
            if "metadata" in name.lower():
                continue
        except OSError:
            pass
        nodes.append(path)
    return nodes


def _usb_id_model(dev_path):
    """ID_MODEL del USB padre (ej. Streamplify_CAM), o ''."""
    import subprocess
    try:
        out = subprocess.check_output(
            ["udevadm", "info", "--query=all", "--name=" + dev_path],
            timeout=5).decode()
    except Exception:
        return ""
    for line in out.splitlines():
        if line.startswith("E: ID_MODEL="):
            return line.split("=", 1)[1]
    return ""


def resolver_camara(order):
    """Resuelve la primera fuente disponible de una lista ordenada.

    Entradas: 'mipi' (solo trampa ESP-IDF: aquí se salta con aviso),
    'usb:<nombre>' (match por ID_MODEL USB, ej. streamplify),
    'usb:any' (primer video que abra), índice ('4') o ruta (/dev/video4).

    Returns:
        int | str: índice/ruta OpenCV lista para VideoCapture.
    """
    for src in [s.strip() for s in order.split(",") if s.strip()]:
        low = src.lower()
        if low == "mipi":
            print("cam: mipi no disponible en laptop (vive en el firmware ESP-IDF)")
            continue
        if low.startswith("usb:"):
            want = low[4:]
            for node in _video_nodes():
                if want in ("any", "*") or want in _usb_id_model(node).lower():
                    print("cam: %s (%s)" % (node, _usb_id_model(node) or "?"))
                    return node
            continue
        return int(src) if src.isdigit() else src
    raise RuntimeError("ninguna fuente de cámara disponible en: %s" % order)


def to_qimage(frame):
    """Convierte un frame BGR de OpenCV a QImage (puente Qt).

    OpenCV captura y Qt muestra: QVideoWidget no queda excluido, solo
    que PySide6 es opcional (no instalado en todos los hosts).
    Devuelve None si PySide6 no está disponible.
    """
    try:
        from PySide6.QtGui import QImage
    except ImportError:
        return None
    import cv2
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = rgb.shape
    return QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()


def draw_detections(jpeg_bytes, detections, threshold=0.5):
    """Dibuja cajas + veredicto sobre el JPEG (PIL, sin GUI).

    Verde = clase prioritaria sobre umbral (ES broca), rojo = resto.
    Las cajas vienen en el formato normalizado de /api/detect
    (x,y centro + width/height en píxeles, como las entrega RF-DETR
    vía Roboflow). Devuelve JPEG anotado.
    """
    import io
    from PIL import Image, ImageDraw

    img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
    d = ImageDraw.Draw(img)
    W, H = img.size
    hay = False
    for p in detections or []:
        conf = p.get("confidence") or 0
        bb = p.get("bbox") or {}
        try:
            x, y = float(bb.get("x", 0)), float(bb.get("y", 0))
            w, h = float(bb.get("width", 0)), float(bb.get("height", 0))
        except (TypeError, ValueError):
            continue
        ok = conf >= threshold
        hay = hay or ok
        color = (0, 255, 0) if ok else (255, 0, 0)
        d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2],
                    outline=color, width=3)
        d.text((x - w / 2 + 2, max(y - h / 2 - 12, 0)),
               "%s %.0f%%" % (p.get("class"), 100 * conf), fill=color)
    d.rectangle([0, 0, W, 24], fill=(0, 0, 0))
    d.text((6, 5), "BROCA %.0f%%" % (100 * max(
        [(p.get("confidence") or 0) for p in (detections or [])] + [0]))
        if hay else "NO ES BROCA", fill=(0, 255, 0) if hay else (255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _jpeg_a_frame(jpeg_bytes):
    """Decodifica JPEG a frame BGR (para preview anotado)."""
    import cv2
    import numpy as np
    return cv2.imdecode(np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)


def preview_frame(frame, ms=1500, titulo="trampa (cierra para seguir)"):
    """Muestra un frame con OpenCV (Q/ESC lo cierra antes)."""
    import cv2
    cv2.imshow(titulo, frame)
    cv2.waitKey(ms)
    cv2.destroyAllWindows()


def foto_camara(indice=0, ancho=1920, alto=1080, preview=False):
    """Un frame de la webcam local (OpenCV). Para validar con imagen real."""
    import cv2

    cap = cv2.VideoCapture(indice)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError("webcam %d no entregó frame" % indice)
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return bytes(buf)


def foto_archivo(ruta):
    """Foto real desde disco (ej. la broca del teléfono ya copiada)."""
    with open(ruta, "rb") as f:
        return f.read()


def telemetria(i):
    return {
        "trap_id": TRAP_ID,
        "temp_c": round(24.0 + 0.3 * i, 1),
        "hum_pct": 78,
        "count": i,
        "rssi_dbm": -70 - i,
        "lux": 45000.0,
        "cebo_ml": round(480.0 - 0.5 * i, 1),
        "cebo_low": False,
    }


def post_foto(jpeg):
    boundary = "simtrampa123"
    body = (
        ("--%s\r\nContent-Disposition: form-data; name=\"trap_id\"\r\n\r\n%s\r\n"
         % (boundary, TRAP_ID)).encode()
        + ("--%s\r\nContent-Disposition: form-data; name=\"file\"; "
           "filename=\"sim.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n" % boundary).encode()
        + jpeg + b"\r\n--%s--\r\n" % boundary.encode()
    )
    req = urllib.request.Request(
        API + "/api/fotos", data=body,
        headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary,
                 "X-Trap-Key": TRAP_KEY},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode())


def post_detect(jpeg):
    body = json.dumps({
        "trap_id": TRAP_ID,
        "image_base64": base64.b64encode(jpeg).decode(),
    }).encode()
    req = urllib.request.Request(
        API + "/api/detect", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tele", type=int, default=5)
    ap.add_argument("--fotos", type=int, default=2)
    ap.add_argument("--foto", default="",
                    help="ruta a foto real (ej. broca del teléfono) en vez de sintética")
    ap.add_argument("--cam", action="store_true",
                    help="captura de cámara real en vez de sintética")
    ap.add_argument("--cam-index", type=int, default=4,
                    help="OBSOLETO: usar --cam-order (se mantiene por compat)")
    ap.add_argument("--cam-order", default="",
                    help="prioridad: mipi,usb:streamplify,usb:any (MIPI solo en trampa)")
    ap.add_argument("--preview", action="store_true",
                    help="muestra cada captura en ventana (Q/ESC cierra)")
    ap.add_argument("--annotate", action="store_true",
                    help="infiere por foto y muestra cajas + veredicto BROCA/NO (requiere keys)")
    ap.add_argument("--min-conf", type=float, default=0.5,
                    help="umbral de confianza del veredicto")
    args = ap.parse_args()

    import os as _os
    order = args.cam_order or _os.getenv("CAM_ORDER", "mipi,usb:streamplify,usb:any")
    cam_src = resolver_camara(order) if args.cam else None
    preview = bool(args.preview)

    def fuente(i):
        if args.foto:
            return foto_archivo(args.foto)
        if args.cam:
            return foto_camara(cam_src, preview=preview)
        return foto_jpeg("BROCA-SIM-%d" % i)

    for i in range(args.tele):
        payload = telemetria(i)
        publish.single(
            f"agrivision/demo/{TRAP_ID}/telemetry", json.dumps(payload),
            hostname=MQTT_HOST, port=MQTT_PORT,
        )
        print("mqtt %d/%d ok" % (i + 1, args.tele))
        time.sleep(0.5)

    for i in range(args.fotos):
        jpeg = fuente(i)
        if args.annotate:
            st, det = post_detect(jpeg)
            if st == 201:
                jpeg_view = draw_detections(jpeg, det.get("detections"), args.min_conf)
                print("detect: %s broca=%s" % (
                    det.get("model"),
                    any((p.get("confidence") or 0) >= args.min_conf
                        for p in det.get("detections", []))))
            else:
                jpeg_view = jpeg
                print("detect: %s (sin anotar)" % det.get("detail"))
            if args.preview:
                preview_frame(_jpeg_a_frame(jpeg_view),
                              titulo="det #%d (Q/ESC sigue)" % (i + 1))
        st, meta = post_foto(jpeg)
        print("foto %d: %s id=%s size=%s" % (i + 1, st, meta["id"], meta["size_bytes"]))

    if not args.annotate:
        st, out = post_detect(fuente(99))
        print("detect: %s %s" % (st, out.get("detail", out.get("model", out))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
