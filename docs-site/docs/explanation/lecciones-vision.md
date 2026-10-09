---
sidebar_position: 3
---

# Lecciones aprendidas: visión con SAM 3

Evidencia de la validación live (Streamplify + backend + workflow `agrivision-demo-hackathon-5g-2026`, oct-2026).

## 1. Publicar el Workflow antes de probar por API

El editor mostraba "Draft saved — not published yet" y la API devolvía 0 detecciones. La API ejecuta la versión publicada: **Publish primero**, reintentar después.

## 2. Foto de pantalla ≠ archivo original

El mismo workflow sobre el archivo original: `broca-cafe` 0.816 + polígono de 170 pts (verificado por CLI directo y por `/api/detect`). Sobre la foto que la webcam toma del teléfono (brillo, moiré, rotación, menos resolución efectiva): 0 detecciones. Para la demo usar archivos originales o captura directa sin reflejos.

## 3. Base64 sí vale para `run_workflow`

`inputs.image = {"type": "base64", "value": ...}` funciona igual que URL. El backend lo usa así y el resultado es idéntico al del CLI.

## 4. SAM no da confianza: se asume 1.0

Las predicciones SAM traen clase + geometría pero no siempre `confidence`. El backend la assume 1.0 para que umbrales, alertas y Telegram operen igual que con un modelo entrenado.

## 5. Los polígonos fluyen de punta a punta

`points` del workflow → `detections[].polygon` en la API → dibujo de contorno en sim/consola → panel Business Media en Grafana. No botarlos: en un insecto de 2 mm el contorno vale más que la caja.

## 6. Una cámara, un dueño

v4l2 en exclusivo: la consola Qt, el sim y el CLI no pueden abrir la Streamplify a la vez. Cerrar la consola antes de simular por script y viceversa.

## 7. Para la demo por webcam: fotos impresas en mate

La foto-de-pantalla falla por moiré + brillo + refresco (0 detecciones donde el archivo original da 0.82–0.94). Imprimir las fotos validadas en papel mate (~10–15 cm) y mostrarlas a 20–30 cm de la cámara elimina las tres fuentes a la vez; el glossy mete reflejos propios. Sin impresora: pantalla completa con brillo alto en cuarto oscuro (reduce, no elimina).

## 8. RCA: 503 por key perdida tras recreate (no fallar mañana)

Síntoma: `Detectar` → 503 aunque la key "ya estaba puesta". Causas:

1. La key vivía solo en el entorno del contenedor al crearlo (`secret-use ... up`): cualquier `up` posterior sin el secret la borraba.
2. Trampa de precedencia de compose: `ROBOFLOW_API_KEY: ${...:-}` vacío en `environment:` **pisa** al `env_file` aunque el archivo tenga la key.

Fix: `.roboflow.env` (0600, gitignoreado) + `env_file: required: false` en el servicio backend + **no declarar** la variable en `environment:`. Checklist pre-demo: `curl localhost:8000/health` debe decir `roboflow.configured: true`; si dice false, ni probar detección.

## 9. Still full-res, no grab del widget (QImageCapture)

El `grab()` del `QVideoWidget` sale a resolución de pantalla (~640 px) y SAM no ve insectos de pocos píxeles. La consola captura con `QImageCapture` sobre la misma `QMediaCaptureSession`: el preview sigue vivo por un canal y el still full-res va al modelo por otro. Por eso hay **dos cuadros**: arriba video vivo (Qt lo pinta, no se puede anotar encima), abajo still anotado. El still es el que viaja a `/api/detect`.

## 10. La "eternidad": el loop anidado necesita su propio quit

`QImageCapture.capture()` es asíncrono: se entra a un `QEventLoop` local con `QTimer.singleShot(8000, loop.quit)` como timeout de seguridad. Los 8 s **no** son espera fija — pero el primer código no llamaba `loop.quit()` en el callback `imageCaptured`, así que siempre esperaba los 8 s completos. Fix: `loop.quit()` dentro de `_done` + `dlog` del tiempo real de still (típico 0.0–0.3 s). Misma sesión salió un `NameError: lay` porque los métodos del spinner quedaron insertados en medio del `__init__` y tragaron la creación de widgets: moraleja de no editar a ciegas sin compilar y revisar el diff. No hay state machine — solo flag `busy` (botones bloqueados + cursor espera + veredicto animado `capturando…/detectando…`); el `finally` siempre vuelve a `idle`.

## 11. Polígono sin tag no existe (a ojos del demo)

`draw_detections` solo ponía el tag `clase + %` en la rama de cajas; las 9 detecciones SAM vienen todas con polígono (62–158 pts) y quedaban en outline de 1 px, invisible al escalar al thumbnail. Fix en `sim_esp32.py`: `d.line(cerrado, width=max(3, W//240), joint="curve")` + tag `broca-cafe 80%` con `DejaVuSans-Bold` escalada (`H//36`) sobre rectángulo negro. Regla: trazo y fuente escalan con la imagen o no sobreviven al thumbnail.

## 12. Layout: entradas izq, salidas der

Una sola columna mezclaba preview, veredicto, still y debug. Ahora: izq = dropdown + Re-scan + preview vivo + Foto/Detectar; der = veredicto + resumen + still anotado + debug colapsable (`▶/▼ debug` con tiempos, tamaños y top-8 por confianza).

## 13. Grafana: base64 crudo no rinde, va data-URL

El panel `volkovlabs-image-panel` no muestra el base64 pelado: la query debe prefijar el MIME de la fila — `('data:' || content_type || ';base64,' || encode(data,'base64')) AS foto`. Sin el prefijo, panel gris sin error visible.
