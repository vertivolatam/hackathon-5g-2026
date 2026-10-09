"""Anotación de detecciones sobre JPEG (Pillow).

Espejo de ``scripts/sim_esp32.py:draw_detections``: el sim no corre dentro
del contenedor, así que la lógica vive duplicada a propósito — mantener
ambas iguales (trazo escalado + tag con fondo, ver lección 11).

Se usa para la foto que viaja a Telegram: la alerta muestra los mismos
polígonos y tags que la consola Qt.
"""

import io


def annotate_detections(jpeg_bytes, detections, min_conf=0.5):
    """Dibuja polígonos/cajas + tags + veredicto. Devuelve JPEG anotado."""
    from PIL import Image, ImageDraw

    img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
    d = ImageDraw.Draw(img)
    W, H = img.size
    lw = max(3, W // 240)
    try:
        from PIL import ImageFont

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            max(18, H // 36))
    except Exception:
        try:
            from PIL import ImageFont

            font = ImageFont.load_default(size=max(18, H // 36))
        except Exception:
            font = None
    hay = False

    def _tag(xy, txt, color):
        if font is None:
            d.text(xy, txt, fill=color)
            return
        l, t, r, b = d.textbbox(xy, txt, font=font)
        d.rectangle([l - 3, t - 2, r + 3, b + 2], fill=(0, 0, 0))
        d.text(xy, txt, fill=color, font=font)

    for p in detections or []:
        conf = p.get("confidence") or 0
        ok = conf >= min_conf
        hay = hay or ok
        color = (0, 255, 0) if ok else (255, 0, 0)
        tag = "%s %.0f%%" % (p.get("class"), 100 * conf)
        poly = p.get("polygon")
        if poly and len(poly) >= 3:
            flat = [(float(x), float(y)) for x, y in poly]
            d.line(flat + [flat[0]], fill=color, width=lw, joint="curve")
            xs = [x for x, _ in flat]
            ys = [y for _, y in flat]
            _tag((min(xs) + 2, max(min(ys) - (30 if font else 14), 0)), tag, color)
        else:
            bb = p.get("bbox") or {}
            try:
                x, y = float(bb.get("x", 0)), float(bb.get("y", 0))
                w, h = float(bb.get("width", 0)), float(bb.get("height", 0))
            except (TypeError, ValueError):
                continue
            d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2],
                        outline=color, width=lw)
            _tag((x - w / 2 + 2, max(y - h / 2 - (30 if font else 14), 0)), tag, color)
    top = max([(p.get("confidence") or 0) for p in (detections or [])] + [0])
    d.rectangle([0, 0, W, 26], fill=(0, 0, 0))
    d.text((6, 5), "BROCA %.0f%%" % (100 * top) if hay else "NO ES BROCA",
           fill=(0, 255, 0) if hay else (255, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()
