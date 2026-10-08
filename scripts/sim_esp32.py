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
    args = ap.parse_args()

    for i in range(args.tele):
        payload = telemetria(i)
        publish.single(
            f"agrivision/demo/{TRAP_ID}/telemetry", json.dumps(payload),
            hostname=MQTT_HOST, port=MQTT_PORT,
        )
        print("mqtt %d/%d ok" % (i + 1, args.tele))
        time.sleep(0.5)

    for i in range(args.fotos):
        jpeg = foto_jpeg("BROCA-SIM-%d" % i)
        st, meta = post_foto(jpeg)
        print("foto %d: %s id=%s size=%s" % (i + 1, st, meta["id"], meta["size_bytes"]))

    st, out = post_detect(foto_jpeg("DETECT"))
    print("detect: %s %s" % (st, out.get("detail", out.get("model", out))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
