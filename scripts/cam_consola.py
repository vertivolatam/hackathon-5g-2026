"""Consola de operador de la trampa (PySide6 + QVideoWidget).

Muestra el video en vivo, captura fotos a /api/fotos e infiere con
/anotación de cajas + veredicto BROCA/NO (igual que sim --annotate).

Pipeline preferido: QCamera -> QVideoWidget (Qt Multimedia). Si el
backend Qt no ve la cámara, cae a OpenCV + QLabel sin cambiar la UI.

Uso:
    python3 scripts/cam_consola.py [--api http://localhost:8000]
Requiere: pip install PySide6 (el backend Qt Multimedia viene incluido).
"""

import argparse
import base64
import io
import json
import sys
import time
import traceback
import urllib.request
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
    QPushButton, QVBoxLayout, QWidget,
)

try:
    from PySide6.QtMultimedia import QCamera, QImageCapture, QMediaCaptureSession, QMediaDevices
    from PySide6.QtMultimediaWidgets import QVideoWidget
    QT_VIDEO_OK = True
except ImportError:  # Qt sin backend multimedia: solo QLabel
    QT_VIDEO_OK = False


class Consola(QMainWindow):
    def __init__(self, api, cam_order):
        super().__init__()
        self.api = api.rstrip("/")
        self.setWindowTitle("AgriVision · Consola de trampa")
        self.resize(900, 640)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        self.video = None
        self.camera = None
        self.session = None
        self.cap = None
        self.timer = None
        self.img = None
        self._qt_list = []
        self._still = None  # QImageCapture: foto full-res, no grab del widget

        from PySide6.QtWidgets import QComboBox, QPushButton as _PB

        top = QHBoxLayout()
        self.cam_combo = QComboBox()
        self.cam_combo.currentIndexChanged.connect(self._on_cam_changed)
        top.addWidget(self.cam_combo, stretch=1)
        b_scan = _PB("Re-scan")
        b_scan.clicked.connect(self._fill_cameras)
        top.addWidget(b_scan)
        lay.addLayout(top)

        self._cam_order = cam_order
        self._vid_slot = QVBoxLayout()
        lay.addLayout(self._vid_slot, stretch=1)
        self._fill_cameras()

        self.veredicto = QLabel("—")
        self.veredicto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.veredicto.setStyleSheet("font-size: 28px; font-weight: bold;")
        lay.addWidget(self.veredicto)

        btns = QHBoxLayout()
        self.b_foto = QPushButton("Foto → /api/fotos")
        self.b_foto.clicked.connect(self.on_foto)
        self.b_det = QPushButton("Detectar (cajas + veredicto)")
        self.b_det.clicked.connect(self.on_detectar)
        btns.addWidget(self.b_foto)
        btns.addWidget(self.b_det)
        lay.addLayout(btns)

        # Spinner de ocupado: puntos animados + cursor de espera mientras
        # el still o el POST al modelo bloquean (el loop anidado sí
        # procesa eventos, así que el texto anima).
        self._spin = QTimer(self)
        self._spin.timeout.connect(self._tick_spin)
        self._spin_n = 0
        self._spin_msg = ""

        self.log = QLabel("listo")
        lay.addWidget(self.log)

        # Última foto anotada (en modo Qt el preview sigue vivo: el still
        # con cajas se muestra aquí, no sobre el video).
        self.shot = QLabel("sin captura anotada")
        self.shot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shot.setMinimumHeight(180)
        self.shot.setStyleSheet("border: 1px solid #555;")
        lay.addWidget(self.shot)

        # Bloque colapsable de debug: cada Detectar/Foto deja traza con
        # tiempos, tamaños y errores (ver dlog).
        self.dbg_toggle = QPushButton("▶ debug")
        self.dbg_toggle.setCheckable(True)
        self.dbg_toggle.toggled.connect(self._on_dbg_toggled)
        lay.addWidget(self.dbg_toggle)
        self.dbg = QPlainTextEdit()
        self.dbg.setReadOnly(True)
        self.dbg.setMaximumBlockCount(300)
        self.dbg.setPlaceholderText("log de debug: captura, POST, tiempos, errores…")
        self.dbg.setVisible(False)
        self.dbg.setMinimumHeight(140)
        lay.addWidget(self.dbg)

    def _tick_spin(self):
        self._spin_n = (self._spin_n + 1) % 4
        dots = "." * (self._spin_n + 1)
        self.veredicto.setText("%s%s" % (self._spin_msg, dots))
        self.veredicto.setStyleSheet("font-size: 28px; color: orange;")

    def _set_busy(self, on, msg="trabajando"):
        """Bloquea botones + cursor espera + veredicto animado. No lanza."""
        try:
            from PySide6.QtWidgets import QApplication

            self.b_foto.setEnabled(not on)
            self.b_det.setEnabled(not on)
            if on:
                self._spin_msg = msg
                self._spin_n = 0
                self._tick_spin()
                self._spin.start(250)
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            else:
                self._spin.stop()
                try:
                    QApplication.restoreOverrideCursor()
                except Exception:
                    pass
            QApplication.processEvents()
        except Exception as e:
            print("busy(%s) falló: %s" % (on, e))

    def _on_dbg_toggled(self, on):
        self.dbg.setVisible(on)
        self.dbg_toggle.setText("▼ debug" if on else "▶ debug")

    def dlog(self, msg):
        """Una línea con hora al bloque debug + resumen en self.log."""
        line = "%s %s" % (datetime.now().strftime("%H:%M:%S"), msg)
        print(line)
        try:
            self.dbg.appendPlainText(line)
        except Exception:
            pass
        self.log.setText(msg[:220])

    # -- selección de cámara ------------------------------------------
    def _qt_cams(self):
        if not QT_VIDEO_OK:
            return []
        try:
            return list(QMediaDevices.videoInputs())
        except Exception:
            return []

    def _fill_cameras(self):
        """Llena el dropdown: cámaras Qt por nombre + modo OpenCV auto."""
        self.cam_combo.blockSignals(True)
        self.cam_combo.clear()
        self._qt_list = self._qt_cams()
        for c in self._qt_list:
            self.cam_combo.addItem("Qt: " + c.description())
        self.cam_combo.addItem("OpenCV: auto (%s)" % self._cam_order)
        self.cam_combo.blockSignals(False)
        if self.cam_combo.count():
            self._on_cam_changed(0)

    def _clear_video(self):
        try:
            if self.camera is not None:
                self.camera.stop()
        except Exception:
            pass
        if self.timer is not None:
            self.timer.stop()
            self.timer = None
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        self.camera = None
        self.session = None
        self.video = None
        self.img = None
        self._still = None
        while self._vid_slot.count():
            w = self._vid_slot.takeAt(0).widget()
            if w is not None:
                w.deleteLater()

    def _on_cam_changed(self, idx):
        self._clear_video()
        if idx < len(self._qt_list):
            c = self._qt_list[idx]
            try:
                self.video = QVideoWidget()
                self._vid_slot.addWidget(self.video)
                self.camera = QCamera(c)
                self.session = QMediaCaptureSession()
                self.session.setCamera(self.camera)
                self.session.setVideoOutput(self.video)
                # Still full-res para foto/detect (el grab del widget sale
                # chico y SAM no ve insectos de pocos píxeles).
                self._still = QImageCapture(self.camera)
                self.session.setImageCapture(self._still)
                self.camera.start()
                print("video: QCamera + QVideoWidget (%s)" % c.description())
                return
            except Exception as e:
                print("QCamera falló (%s): uso OpenCV" % e)
                self._clear_video()
        from sim_esp32 import resolver_camara  # noqa
        import cv2

        try:
            self.cap = cv2.VideoCapture(resolver_camara(self._cam_order))
        except Exception as e:
            print("sin cámaras: %s" % e)
            self.img = QLabel("sin cámaras (conecta una y pulsa Re-scan)")
            self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._vid_slot.addWidget(self.img)
            return
        self.img = QLabel("sin video")
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._vid_slot.addWidget(self.img)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick_opencv)
        self.timer.start(66)  # ~15 fps
        print("video: OpenCV + QLabel")

    # -- captura ------------------------------------------------------
    def frame_jpeg(self):
        if self.cap is not None:
            import cv2

            ok, frame = self.cap.read()
            if not ok:
                raise RuntimeError("cámara no entregó frame")
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return bytes(buf)
        if self.video is None or self._still is None:
            raise RuntimeError("sin cámara activa (elige una en el dropdown)")
        # Still full-res (el grab del widget sale chico para SAM).
        from PySide6.QtCore import QBuffer, QEventLoop, QIODevice, QTimer

        got = {}
        loop = QEventLoop()

        def _done(req_id, img):
            got["img"] = img
            loop.quit()  # sin esto: espera los 8 s fijos (la "eternidad")

        self._still.imageCaptured.connect(_done)
        try:
            QTimer.singleShot(8000, loop.quit)
            t0 = time.time()
            self._still.capture()
            loop.exec()
            self._last_still_s = time.time() - t0
        finally:
            try:
                self._still.imageCaptured.disconnect(_done)
            except Exception:
                pass
        if "img" not in got:
            raise RuntimeError("la cámara no entregó still (reintenta)")
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        got["img"].save(buf, "JPG", 88)
        return bytes(buf.data())

    def _tick_opencv(self):
        import cv2

        ok, frame = self.cap.read()
        if not ok:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
        self.img.setPixmap(QPixmap.fromImage(img).scaled(
            self.img.size(), Qt.AspectRatioMode.KeepAspectRatio))

    # -- backend ------------------------------------------------------
    def _post(self, path, body, headers):
        req = urllib.request.Request(self.api + path, data=body,
                                     headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())

    def _show_shot(self, jpeg_bytes, caption=""):
        """Pinta la foto anotada en el QLabel inferior (ambos modos)."""
        img = QImage.fromData(jpeg_bytes, "JPG")
        if img.isNull():
            self.dlog("shot: QImage no pudo decodificar (%d bytes) %s"
                      % (len(jpeg_bytes), caption))
            return
        pm = QPixmap.fromImage(img).scaled(
            self.shot.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.shot.setPixmap(pm)
        self.shot.setText("")

    def on_foto(self):
        self._set_busy(True, "capturando")
        try:
            t0 = time.time()
            jpeg = self.frame_jpeg()
            still_s = getattr(self, "_last_still_s", 0) or 0
            self.dlog("foto: still %d bytes en %.1fs (modo %s)"
                      % (len(jpeg), still_s if self.cap is None else time.time() - t0,
                         "opencv" if self.cap is not None else "qt-still"))
            boundary = "consola1"
            body = (
                ("--%s\r\nContent-Disposition: form-data; name=\"trap_id\"\r\n\r\n"
                 "trap-edge\r\n" % boundary).encode()
                + ("--%s\r\nContent-Disposition: form-data; name=\"file\"; "
                   "filename=\"consola.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n"
                   % boundary).encode()
                + jpeg + ("\r\n--%s--\r\n" % boundary).encode())
            t1 = time.time()
            st, meta = self._post("/api/fotos", body, {
                "Content-Type": "multipart/form-data; boundary=%s" % boundary,
                "X-Trap-Key": "dev-trap-key"})
            self.dlog("foto: POST /api/fotos -> %s id=%s (%s bytes) en %.1fs"
                      % (st, meta.get("id"), meta.get("size_bytes"), time.time() - t1))
        except Exception as e:
            self.dlog("foto ERROR: %s\n%s" % (e, traceback.format_exc(limit=3)))
        finally:
            self._set_busy(False)

    def on_detectar(self):
        self._set_busy(True, "capturando")
        try:
            from sim_esp32 import draw_detections  # noqa

            t0 = time.time()
            jpeg = self.frame_jpeg()
            still_s = getattr(self, "_last_still_s", 0) or 0
            self.dlog("detectar: still %d bytes en %.1fs (modo %s)"
                      % (len(jpeg), still_s if self.cap is None else time.time() - t0,
                         "opencv" if self.cap is not None else "qt-still"))
            self._set_busy(True, "detectando")
            t1 = time.time()
            st, out = self._post("/api/detect", json.dumps({
                "trap_id": "trap-edge",
                "image_base64": base64.b64encode(jpeg).decode(),
            }).encode(), {"Content-Type": "application/json"})
            dt = time.time() - t1
            if st != 201:
                self.veredicto.setText("SIN MODELO (%s)" % out.get("detail", st))
                self.veredicto.setStyleSheet("font-size: 28px; color: orange;")
                self.dlog("detectar: POST /api/detect -> %s en %.1fs: %s"
                          % (st, dt, str(out)[:300]))
                return
            preds = out.get("detections", [])
            top = max([p.get("confidence", 0) for p in preds] + [0])
            es = top >= 0.5
            self.veredicto.setText("ES BROCA %.0f%%" % (100 * top) if es else "NO ES BROCA")
            self.veredicto.setStyleSheet(
                "font-size: 28px; font-weight: bold; color: %s;"
                % ("green" if es else "red"))
            for p in sorted(preds, key=lambda d: -d.get("confidence", 0))[:8]:
                self.dlog("  - %s %.3f poly=%dpts"
                          % (p.get("class"), p.get("confidence", 0),
                             len(p.get("polygon") or [])))
            anot = draw_detections(jpeg, preds, 0.5)
            self._show_shot(anot)
            if self.cap is not None:
                # Además refresca el preview OpenCV con las cajas.
                from sim_esp32 import _jpeg_a_frame  # noqa

                frame = _jpeg_a_frame(anot)
                import cv2

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = rgb.shape
                img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
                self.img.setPixmap(QPixmap.fromImage(img).scaled(
                    self.img.size(), Qt.AspectRatioMode.KeepAspectRatio))
            self.dlog("detectar OK: modelo %s, %d detecciones, top=%.2f en %.1fs total"
                      % (out.get("model"), len(preds), top, time.time() - t0))
        except Exception as e:
            self.dlog("detectar ERROR: %s\n%s" % (e, traceback.format_exc(limit=3)))
        finally:
            self._set_busy(False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--cam-order", default="mipi,usb:streamplify,usb:any")
    args = ap.parse_args()
    app = QApplication(sys.argv)
    w = Consola(args.api, args.cam_order)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
