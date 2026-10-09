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


class Estado:
    """State machine de la consola (lección 10).

    IDLE -> CAPTURANDO -> DETECTANDO -> IDLE; cualquier excepción -> ERROR.
    Toda transición queda en el debug: un atascado se diagnostica por el
    último estado, no adivinando un boolean.
    """

    IDLE = "idle"
    CAPTURANDO = "capturando"
    DETECTANDO = "detectando"
    ERROR = "error"


class Consola(QMainWindow):
    def __init__(self, api, cam_order):
        super().__init__()
        self.api = api.rstrip("/")
        self.setWindowTitle("AgriVision · Consola de trampa")
        self.resize(900, 640)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        cols = QHBoxLayout()
        lay.addLayout(cols, stretch=1)
        from PySide6.QtWidgets import QVBoxLayout as _VL

        left = _VL()   # inputs: cámara + preview vivo + acciones
        right = _VL()  # outputs: veredicto + still anotado + log + debug
        cols.addLayout(left, stretch=1)
        cols.addLayout(right, stretch=1)

        self.video = None
        self.camera = None
        self.session = None
        self.cap = None
        self.timer = None
        self.img = None
        self._qt_list = []
        self._still = None  # QImageCapture: foto full-res, no grab del widget
        # Watchdog de tirón de cable: latch para avisar UNA vez por
        # desconexión (y otra al recuperarse), no en cada tick fallido.
        # ANTES del primer _fill_cameras: _on_cam_changed ya los toca.
        self._sin_camara = False
        self._fails = 0
        # Detector de freeze (Qt congela el frame sin avisar al tirar
        # del cable): hash 1 Hz del preview; 5 iguales seguidos = alerta.
        # ANTES del primer _fill_cameras (igual que el latch).
        self._freeze_timer = None
        self._frozen_hash = None
        self._frozen_n = 0
        # El dispositivo se fue de la lista y no volvió: solo entonces el
        # auto-reopen toca la cámara (si no, un stall/static reabre en loop
        # y spamea ✅ al grupo).
        self._ausente = False
        # Anti-spam demo: tras una recuperada, 30 s sin re-avisar por
        # freeze (las señales duras —error/dispositivo/OpenCV— sí avisan).
        self._cooldown_hasta = 0.0

        from PySide6.QtWidgets import QComboBox, QLabel as _L, QPushButton as _PB

        left.addWidget(_L("Entradas · cámara y captura"))
        top = QHBoxLayout()
        self.cam_combo = QComboBox()
        self.cam_combo.currentIndexChanged.connect(self._on_cam_changed)
        top.addWidget(self.cam_combo, stretch=1)
        b_scan = _PB("Re-scan")
        b_scan.clicked.connect(self._fill_cameras)
        top.addWidget(b_scan)
        left.addLayout(top)

        self._cam_order = cam_order
        self._vid_slot = QVBoxLayout()
        left.addLayout(self._vid_slot, stretch=1)
        try:
            # Tirón de cable en modo Qt: la lista de dispositivos cambia.
            QMediaDevices.videoInputsChanged.connect(self._on_devices_changed)
        except Exception:
            pass
        self._fill_cameras()

        btns = QHBoxLayout()
        self.b_foto = QPushButton("Foto → /api/fotos")
        self.b_foto.clicked.connect(self.on_foto)
        self.b_det = QPushButton("Detectar (cajas + veredicto)")
        self.b_det.clicked.connect(self.on_detectar)
        btns.addWidget(self.b_foto)
        btns.addWidget(self.b_det)
        left.addLayout(btns)

        # Spinner de ocupado: puntos animados + cursor de espera mientras
        # el still o el POST al modelo bloquean (el loop anidado sí
        # procesa eventos, así que el texto anima).
        self._spin = QTimer(self)
        self._spin.timeout.connect(self._tick_spin)
        self._spin_n = 0
        self._spin_msg = ""
        self.estado = Estado.IDLE

        right.addWidget(_L("Salidas · veredicto y evidencia"))
        self.veredicto = QLabel("—")
        self.veredicto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.veredicto.setStyleSheet("font-size: 28px; font-weight: bold;")
        right.addWidget(self.veredicto)

        self.log = QLabel("listo")
        self.log.setWordWrap(True)
        right.addWidget(self.log)

        # Última foto anotada (en modo Qt el preview sigue vivo: el still
        # con cajas se muestra aquí, no sobre el video).
        self.shot = QLabel("sin captura anotada")
        self.shot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shot.setMinimumHeight(180)
        self.shot.setStyleSheet("border: 1px solid #555;")
        right.addWidget(self.shot, stretch=1)

        # Bloque colapsable de debug: cada Detectar/Foto deja traza con
        # tiempos, tamaños y errores (ver dlog).
        self.dbg_toggle = QPushButton("▶ debug")
        self.dbg_toggle.setCheckable(True)
        self.dbg_toggle.toggled.connect(self._on_dbg_toggled)
        right.addWidget(self.dbg_toggle)
        self.dbg = QPlainTextEdit()
        self.dbg.setReadOnly(True)
        self.dbg.setMaximumBlockCount(300)
        self.dbg.setPlaceholderText("log de debug: captura, POST, tiempos, errores…")
        self.dbg.setVisible(False)
        self.dbg.setMinimumHeight(140)
        right.addWidget(self.dbg)

    def _tick_spin(self):
        self._spin_n = (self._spin_n + 1) % 4
        dots = "." * (self._spin_n + 1)
        self.veredicto.setText("%s%s" % (self._spin_msg, dots))
        self.veredicto.setStyleSheet("font-size: 28px; color: orange;")

    def _set_estado(self, nuevo, detalle=""):
        """Transición explícita: botones + cursor + spinner + traza. No lanza."""
        try:
            from PySide6.QtWidgets import QApplication

            anterior = self.estado
            self.estado = nuevo
            self.dlog("estado: %s -> %s %s" % (anterior, nuevo, detalle[:80]))
            ocupado = nuevo in (Estado.CAPTURANDO, Estado.DETECTANDO)
            self.b_foto.setEnabled(not ocupado)
            self.b_det.setEnabled(not ocupado)
            if ocupado:
                self._spin_msg = nuevo
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
                if nuevo == Estado.ERROR:
                    self.veredicto.setText("error: %s" % (detalle[:60] or "ver debug"))
                    self.veredicto.setStyleSheet("font-size: 28px; color: orange;")
            QApplication.processEvents()
        except Exception as e:
            print("estado(%s) falló: %s" % (nuevo, e))

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
        try:
            # self.log aún no existe si la cámara falla durante el __init__
            # (misma familia que lección 10: nada de widgets antes de crearlos).
            self.log.setText(msg[:220])
        except Exception:
            pass

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
        if self._freeze_timer is not None:
            self._freeze_timer.stop()
            self._frozen_hash = None
            self._frozen_n = 0
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

    def _evento(self, tipo, detalle=""):
        """POST /api/eventos (watchdog). Nunca lanza: es solo aviso."""
        try:
            st, out = self._post("/api/eventos", json.dumps({
                "trap_id": "trap-edge",
                "tipo": tipo,
                "detalle": detalle,
            }).encode(), {"Content-Type": "application/json",
                          "X-Trap-Key": "dev-trap-key"})
            self.dlog("evento %s -> %s %s" % (tipo, st, out))
        except Exception as e:
            self.dlog("evento %s ERROR: %s" % (tipo, e))

    def _perdida(self, detalle, dura=False):
        if not self._sin_camara:
            self._sin_camara = True
            if not dura and time.time() < self._cooldown_hasta:
                self.dlog("watchdog: freeze en cooldown, sin re-aviso (%s)" % detalle)
                return
            self.dlog("watchdog: cámara perdida (%s)" % detalle)
            self._evento("camara-perdida", detalle)

    def _recuperada(self):
        if self._sin_camara:
            self._sin_camara = False
            self._ausente = False
            self._fails = 0
            self._cooldown_hasta = time.time() + 30
            self.dlog("watchdog: cámara de vuelta")
            self._evento("camara-recuperada")

    def _on_cam_changed(self, idx):
        self._clear_video()
        if idx < len(self._qt_list):
            c = self._qt_list[idx]
            try:
                self.video = QVideoWidget()
                self._vid_slot.addWidget(self.video)
                self.camera = QCamera(c)
                self.camera.errorOccurred.connect(self._on_cam_error)
                self.session = QMediaCaptureSession()
                self.session.setCamera(self.camera)
                self.session.setVideoOutput(self.video)
                # Still full-res para foto/detect (el grab del widget sale
                # chico y SAM no ve insectos de pocos píxeles).
                self._still = QImageCapture(self.camera)
                self.session.setImageCapture(self._still)
                self.camera.start()
                print("video: QCamera + QVideoWidget (%s)" % c.description())
                self._recuperada()  # por si venía de un tirón de cable
                self._frozen_hash = None
                self._frozen_n = 0
                if self._freeze_timer is None:
                    self._freeze_timer = QTimer(self)
                    self._freeze_timer.timeout.connect(self._tick_freeze)
                self._freeze_timer.start(1000)  # 1 Hz: barato y suficiente
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
        self._recuperada()

    def _on_cam_error(self, error, msg=""):
        # Tirón de cable en modo Qt: QCamera avisa por señal (vía dura:
        # salta el cooldown porque es evidencia, no sospecha).
        try:
            det = "%s" % (msg or error)
        except Exception:
            det = "camera error"
        self._perdida("Qt: %s" % det[:100], dura=True)

    def _tick_freeze(self):
        """1 Hz: si el preview no cambia en 5 s, la cámara se tiró.

        El feed vivo nunca repite bytes (ruido de sensor); el widget
        congelado sí. Solo en IDLE para no pelear con captura/detect.
        """
        if self.camera is None or self.video is None:
            return
        if self.estado != Estado.IDLE:
            return
        if self._sin_camara:
            # Auto-reopen SOLO si el dispositivo se fue y volvió (flag de
            # ausencia): reabrir por freeze ciego reaviva stalls solos y
            # spamea recuperadas. Cooldown 5 s entre intentos.
            self._frozen_n += 1
            if self._ausente and self._frozen_n % 5 == 0:
                try:
                    vivas = [c.description() for c in self._qt_cams()]
                    actual = self.cam_combo.currentText()
                    if any(v in actual for v in vivas):
                        self.dlog("watchdog: dispositivo de vuelta, reabriendo solo")
                        self._on_cam_changed(self.cam_combo.currentIndex())
                except Exception as e:
                    self.dlog("reopen: %s" % e)
            return
        try:
            from PySide6.QtCore import QBuffer, QIODevice
            import hashlib

            px = self.video.grab()
            if px.isNull():
                return
            buf = QBuffer()
            buf.open(QIODevice.OpenModeFlag.WriteOnly)
            px.scaled(32, 32).toImage().save(buf, "PPM")
            h = hashlib.md5(bytes(buf.data())).hexdigest()
        except Exception:
            return
        if h == self._frozen_hash:
            self._frozen_n += 1
            if self._frozen_n == 5:
                self.dlog("watchdog: preview igual 5s (sospecha, escena estática o stall)")
            if self._frozen_n == 30:
                self._perdida("preview congelado 30s (tirón de cable?)")
        else:
            self._frozen_hash = h
            self._frozen_n = 0
            self._recuperada()

    def _on_devices_changed(self):
        # La cámara activa ya no está enchufada: avisar, no auto-cambiar
        # (el operador elige con Re-scan; evita saltos en plena demo).
        try:
            vivas = [c.description() for c in self._qt_cams()]
            if self.camera is not None:
                actual = self.cam_combo.currentText()
                if not any(v in actual for v in vivas):
                    self._ausente = True
                    self._perdida("USB desconectado (%s)" % actual[:60], dura=True)
        except Exception as e:
            self.dlog("devices-changed: %s" % e)

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

        try:
            ok, frame = self.cap.read()
        except Exception:
            ok, frame = False, None
        if not ok:
            # Racha de reads fallidos = cable fuera (15 ticks ≈ 1 s).
            self._fails += 1
            if self._fails == 15:
                self._perdida("OpenCV: read falló x15", dura=True)
            return
        self._fails = 0
        self._recuperada()
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
        self._set_estado(Estado.CAPTURANDO)
        fallo = ""
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
            fallo = str(e)[:100]
            self.dlog("foto ERROR: %s\n%s" % (e, traceback.format_exc(limit=3)))
        finally:
            self._set_estado(Estado.ERROR if fallo else Estado.IDLE, fallo)

    def on_detectar(self):
        self._set_estado(Estado.CAPTURANDO)
        fallo = ""
        try:
            from sim_esp32 import draw_detections  # noqa

            t0 = time.time()
            jpeg = self.frame_jpeg()
            still_s = getattr(self, "_last_still_s", 0) or 0
            self.dlog("detectar: still %d bytes en %.1fs (modo %s)"
                      % (len(jpeg), still_s if self.cap is None else time.time() - t0,
                         "opencv" if self.cap is not None else "qt-still"))
            self._set_estado(Estado.DETECTANDO)
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
            fallo = str(e)[:100]
            self.dlog("detectar ERROR: %s\n%s" % (e, traceback.format_exc(limit=3)))
        finally:
            self._set_estado(Estado.ERROR if fallo else Estado.IDLE, fallo)


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
