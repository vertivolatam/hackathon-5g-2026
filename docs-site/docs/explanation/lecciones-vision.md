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
