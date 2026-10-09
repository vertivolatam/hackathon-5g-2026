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

## 14. Telegram: token por stash, chat ID a secas

Token (`@BotFather`) vía `/secret-input` → `.telegram.env` (0600, gitignoreado, nunca en logs ni en el commit) + `env_file` en compose, repitiendo el patrón de la lección 8: **nada** de `TELEGRAM_*` en `environment:` o el vacío pisa al archivo. El chat ID del grupo no es secreto: se pega en claro (`TELEGRAM_CHAT_ID=-5191957078`). Sin ambas variables el backend es no-op sin fallar.

## 15. El bot no entra solo: membresía + BotFather

`chat not found` = el bot no es miembro del grupo (agregarlo). `BOT_GROUPS_BLOCKED` = BotFather le prohíbe grupos: `@BotFather` → `/setjoingroups` → Enable (+ `/setprivacy` → Disable para la demo). Verificar sin el backend: `sendMessage` directo a la Bot API debe dar `ok:true` antes de cablear nada.

## 16. Bot ≠ destino

El `@usuario` del bot y su numeric ID no sirven como `TELEGRAM_CHAT_ID`. El destino es el ID negativo del grupo, que da `@getmyid_bot` con *Select group chat*. Tres IDs distintos (usuario, bot, grupo) y solo uno vale.

## 17. La alerta manda foto anotada, no el crudo

El primer push llegaba sin polígonos: `notify` enviaba el `image_b64` original. Fix: `backend/annotate.py` (espejo de `draw_detections` del sim — duplicado a propósito, el sim no corre en el contenedor) anota **antes** de `alert_if_needed`, con `try/except` que devuelve el crudo si Pillow falla: el dibujo nunca rompe la alerta. Costos: `Pillow` en `requirements.txt` + rebuild + `annotate.py` en el `COPY` del Dockerfile (el mount en vivo lo tapa en dev, pero k8s lo necesita).

## 18. Caption legible: finca + trampa, nada más

El slug del workflow (`vertivo-una-huerta...`) y la lista por clase no son para humanos. Caption: `🚨 Broca detectada en <finca> · trampa <id>` + `N broca(s), máx X% (umbral Y%)`. El detalle visual vive en la foto anotada. `finca` viaja en el POST (`cliente/finca/trap_id`) y entra a `build_caption` como parámetro.

## 19. Uvicorn no recarga solo: `make dev-restart`

El código va montado en vivo pero uvicorn corre sin `--reload`: editar un `.py` no cambia nada hasta recrear. Regla: `.py` → `make dev-restart` (recrea sin build + `dev-health`); `requirements.txt`/Dockerfile → `make dev-up` (con `--build`). Tras cada cambio de caption/anotación, restart antes de probar. Y `make hackathon-demo` ahora arranca con `dev-up` + `/health`: la consola apunta al `:8000` y el target nunca lo levantaba (alerta perdida contra backend caído).

## 20. Watchdog en dos niveles: sospecha vs evidencia (anti-spam)

El freeze a 5 s spameó ⚠️/✅ cada 12 s en escena estática (el feed vivo casi no cambia a 32 px) y ante stalls del driver. Diseño final: hash 1 Hz del preview, **sospecha** (solo debug) a 5 s iguales, **aviso** a 30 s; las señales duras (error de QCamera, dispositivo ausente, racha OpenCV) avisan de inmediato y saltan el **cooldown de 30 s** post-recuperada. El auto-reopen solo corre si el dispositivo se fue y volvió (flag de ausencia): reabrir por freeze ciego reavivaba stalls solos y spameaba ✅. Tirón real verificado punta a punta: freeze → `202 notificado:true` → auto-reopen al volver → recuperada, sin Re-scan.
