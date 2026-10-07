# Espacio 3a — Ejecución (Fases 9–13): validación 7-oct-2026

## F9 Modelo ingresos — 🟡 hipótesis, 🔴 números

- Hipótesis (bitácora §11): suscripción plataforma (cliente: cooperativas/equipos técnicos) + instalación, mantenimiento, nodos, análisis avanzados. Dron como complemento futuro, no dependencia.
- Falta: esquema (por nodo/mes vs por asociado vs tarifa plana), precio, quién paga (coop/productor/ambos), y el piloto con gate de resultados como primer precio real.

## F10 Economía unitaria — 🔴

- Falta: costo por nodo (cámara 13 MP + lente + trampa + luz + energía + gateway prorrateado), costo instalación/mantenimiento por visita, margen por suscripción. Sin precio ni costo no hay unit economics.

## F11 Modelo financiero — 🔴

- Bloqueado por F9–F10. Primer insumo realista: costo del MVP físico (1–3 nodos) como capex del piloto.

## F12 Marca e identidad — 🟢 RESUELTO

- Decisión 7-oct: el producto se llama **AgriVision**. Repo, landing, código, docs y MQTT migrados (`BioTrap/BioAgro/RuralIA` → `AgriVision`; topics `agrivision/#`; namespace `agrivision`).
- Queda fuera: identidad visual final (logo, paleta) — la landing actual es placeholder de hackatón.

## F13 Fundación legal — 🔴

- Pregunta: ¿qué figura opera (cooperativa cliente, datos de fincas)?
- Falta: tratamiento de datos de productores (privacidad), responsabilidad ante una señal errada (posicionamiento "apoya, no diagnostica" ayuda pero no sustituye aviso legal), propiedad del dataset de campo (activo moat: ¿de quién son las fotos?).

## Puerta 3 — ¿base financiera y legal sólida? 🔴

Ruta: piloto pagado con métrica (F9) → costos reales del piloto (F10) → figura legal mínima + acuerdo de datos (F13).
