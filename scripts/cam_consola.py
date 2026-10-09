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
import urllib.request

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QVBoxLayout, QWidget,
)

try:
    from PySide6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
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
        b_foto = QPushButton("Foto → /api/fotos")
        b_foto.clicked.connect(self.on_foto)
        b_det = QPushButton("Detectar (cajas + veredicto)")
        b_det.clicked.connect(self.on_detectar)
        btns.addWidget(b_foto)
        btns.addWidget(b_det)
        lay.addLayout(btns)

        self.log = QLabel("listo")
        lay.addWidget(self.log)

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
        if self.video is None:
            raise RuntimeError("sin cámara activa (elige una en el dropdown)")
        # QCamera: snapshot vía captura de pantalla del widget
        from PySide6.QtCore import QBuffer, QIODevice

        px = self.video.grab()
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        px.toImage().save(buf, "JPG", 85)
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

    def on_foto(self):
        try:
            jpeg = self.frame_jpeg()
            boundary = "consola1"
            body = (
                ("--%s\r\nContent-Disposition: form-data; name=\"trap_id\"\r\n\r\n"
                 "trap-edge\r\n" % boundary).encode()
                + ("--%s\r\nContent-Disposition: form-data; name=\"file\"; "
                   "filename=\"consola.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n"
                   % boundary).encode()
                + jpeg + ("\r\n--%s--\r\n" % boundary).encode())
            st, meta = self._post("/api/fotos", body, {
                "Content-Type": "multipart/form-data; boundary=%s" % boundary,
                "X-Trap-Key": "dev-trap-key"})
            self.log.setText("foto %s id=%s (%s bytes)" % (st, meta["id"], meta["size_bytes"]))
        except Exception as e:
            self.log.setText("foto: %s" % e)

    def on_detectar(self):
        try:
            from sim_esp32 import draw_detections  # noqa

            jpeg = self.frame_jpeg()
            st, out = self._post("/api/detect", json.dumps({
                "trap_id": "trap-edge",
                "image_base64": base64.b64encode(jpeg).decode(),
            }).encode(), {"Content-Type": "application/json"})
            if st != 201:
                self.veredicto.setText("SIN MODELO (%s)" % out.get("detail", st))
                self.veredicto.setStyleSheet("font-size: 28px; color: orange;")
                return
            preds = out.get("detections", [])
            top = max([p.get("confidence", 0) for p in preds] + [0])
            es = top >= 0.5
            self.veredicto.setText("ES BROCA %.0f%%" % (100 * top) if es else "NO ES BROCA")
            self.veredicto.setStyleSheet(
                "font-size: 28px; font-weight: bold; color: %s;"
                % ("green" if es else "red"))
            if self.cap is not None:
                from sim_esp32 import _jpeg_a_frame  # noqa

                anot = draw_detections(jpeg, preds, 0.5)
                frame = _jpeg_a_frame(anot)
                import cv2

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = rgb.shape
                img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
                self.img.setPixmap(QPixmap.fromImage(img).scaled(
                    self.img.size(), Qt.AspectRatioMode.KeepAspectRatio))
            self.log.setText("modelo %s, %d detecciones" % (out.get("model"), len(preds)))
        except Exception as e:
            self.log.setText("detectar: %s" % e)


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
