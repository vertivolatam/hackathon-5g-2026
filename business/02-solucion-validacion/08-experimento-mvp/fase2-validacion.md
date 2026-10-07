# Espacio 2 — Solución-Validación (Fases 6–8): validación 7-oct-2026

## F6 Canvas modelo negocio — 🟡 tras este ejercicio

- Ver `06-canvas-modelo-negocio/bmc-agrivision.md` (14 módulos, cada hipótesis marcada 🟢🟡🔴).
- Pregunta: ¿el modelo cierra en papel? Parcial: cierra para segmento bajo presión; para los otros dos depende de módulos (clima/riesgo/boletines) aún no definidos.

## F7 Entrevista solución — 🟡

- Pregunta: ¿compran la solución propuesta (no solo el problema)?
- Evidencia: AgriVision valorado 5/5 (ICAFE), 4/5 (Coopedota, Coopetarrazu); interés en piloto (ICAFE, Coopetarrazu); "probablemente sí" pagarían **si demuestra resultados**.
- Falta: entrevista de solución con precio y métrica de éxito sobre la mesa (el "sí condicional" no es validación comercial).

## F8 Experimento MVP — 🔴 pendiente de ejecutar

- Definición (bitácora §10): 1 cooperativa, café, broca, 1–3 nodos (cámara + trampa + luz), sensores si aportan, Edge AI, 5G SA, dashboard con prioridad, validación final del técnico.
- Flujo demo: captura → Edge → evento/prioridad → 5G → AgriVision → decisión/validación técnica.
- Estado técnico real: telemetría MQTT + API + topics verificados en minikube; detección RF-DETR en PoC local (0.2 s, clase COCO, no broca); detección broca en campo, Edge AI en placa y validación física cámara/lente, pendientes.
- Falta: correr el MVP físico y medir (precisión campo, latencia captura→alerta, tiempo de validación del técnico).

## Puerta 2 — ¿resuelve? ¿pagarían? 🔴

No cruzar hasta: piloto pagado con métrica previa (F7) + MVP físico medido (F8).
