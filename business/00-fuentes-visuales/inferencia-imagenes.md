# Inferencia visual — 4 imágenes (Descargas/hackathons)

Fuente: `~/Descargas/hackathons/*.jpeg` (4 archivos UUID).
Fecha inferencia: 2026-10-06.
Propósito: dejar por escrito lo inferido de las imágenes para refinar el business model después. No reemplaza validación con el equipo.

## IMG-1 — `4cb8ca6c...jpeg` — Infraestructura mínima LoRaWAN → 5G
Título: `AgriVision 5G / AgriVision — Infraestructura mínima para conectar LoRaWAN a la red 5G`.

- Nodos campo (verde = LoRaWAN):
  - Nodo 1: planta / cultivo.
  - Nodo 2: planta + agua (riego / humedad).
  - Nodo 3: finca / granero.
  - Nodo 5: cámara detector broca (trampa con cámara).
- Gateway LoRaWAN Dragino (2 antenas) concentra los 4 nodos.
- Nokia FRRx502e Interior conectado al Dragino.
- Red 5G (Testbed / Laboratorio).
- Nokia FRRO501c Exterior conectado a Red 5G.
- Nodo 4 (morado = nodo fauna): venado + sensor, conectado al FRRO501c.
- Plataforma AgriVision + Edge (nube + servidores) conectada a Red 5G.
- Terminal: Nokia XR20 (rugged) conectado a plataforma.
- Leyenda: verde = LoRaWAN, azul = 5G / Plataforma, morado = nodo fauna.
- Flujo: Nodos → Dragino → FRRx502e → Red 5G → Plataforma → XR20. Fauna va por FRRO501c → Red 5G.

## IMG-2 — `ab6c88c0...jpeg` — Trampa inteligente + sistema punta a punta
4 columnas + 3 bloques inferiores.

1. Trampa inteligente (en la finca):
   - Panel solar (autonomía).
   - Cámara + IA (Inteligencia Artificial) en dispositivo (Edge AI) para identificar broca.
   - Atrayente específico (metanol + etanol).
   - Entrada de captura selectiva (prioriza broca, reduce otros insectos).
   - Batería (días nublados / noche).
   - GPS (Global Positioning System): ubica cada trampa en el mapa.
   - IoT (Internet of Things) (LoRa): envía datos a gateway de la finca (largo alcance, bajo consumo).
   - LoRa (estado, eventos, resúmenes de IA).
2. Gateway 5G (en finca o zona cercana):
   - Recibe datos de varias trampas (LoRa) y los envía por 5G al servidor / edge.
   - 5G: alta velocidad y baja latencia.
3. Edge / Nube (5G Testbed):
   - Servidor Edge / Nube: procesa, almacena y gestiona info de todas las trampas en tiempo real.
   - Análisis con IA (mejora continua del modelo).
   - Almacenamiento de eventos e imágenes.
   - Generación de alertas y recomendaciones.
   - Integración con otros datos (clima, mapas, etc.).
4. Plataforma y usuarios (Web y App):
   - Mapa de trampas en finca (ubicación y estado en tiempo real).
   - Nivel de presencia de broca (historial y tendencias).
   - Alertas tempranas (notificaciones por aumento de actividad).
   - Recomendaciones de manejo (toma de decisiones oportuna).
   - Acceso para productores, técnicos y cooperativas.
   - Mock: laptop con mapa (Trampa 1 Baja, Trampa 2 Media, Trampa 3 Alta) + móvil Trampa 3 alta presencia + gráfico barras.

- Flujo de datos (resumen, 5 pasos):
  Trampa (captura y analiza Edge AI) → Envía datos por LoRa a gateway → Gateway 5G transmite por red 5G → Servidor Edge/Nube procesa, almacena y genera alertas → App/Plataforma visualiza y gestiona.
- Beneficios clave (6): detección temprana, monitoreo en tiempo real, uso eficiente 5G/IoT/Edge, red de múltiples trampas, menor uso insecticidas, mayor productividad y sostenibilidad.
- Escalabilidad: de 1 trampa (MVP — Minimum Viable Product) a red de muchas trampas en finca y otras regiones.

## IMG-3 — `b1e82785...jpeg` — Topología gateways y alcances
Título implícito: Red 5G (Testbed / Laboratorio) como un Wi-Fi al que se conectan los equipos.

- 3 gateways alternativos hacia la misma Red 5G:
  - Nokia FRRO501c (Exterior).
  - Nokia FRRx502e (Interior).
  - Teltonika RUTX11 (4G/5G).
- Terminal: Nokia XR20 (Terminal 5G) directo a Red 5G.
- Bajo cada gateway, misma rama LoRaWAN (verde):
  Sensores LoRaWAN, válvulas de riego, estaciones ambientales, sensores de suelo, otros dispositivos LoRaWAN.
- Alcances declarados en imagen:
  - LoRaWAN (gateway ↔ sensores): 2–15 km según antena, frecuencia, terreno y línea de vista.
  - 5G (equipo ↔ red): hasta varios kilómetros, depende de radio, antena, frecuencia y terreno.
- Implicación: arquitectura multi-gateway intercambiable según interior/exterior o disponibilidad Teltonika.

## IMG-4 — `f0fcc901...jpeg` — Narrativa 7 pasos + valor productor
Título: `AgriVision — Monitoreo inteligente de broca del café. Tecnología 5G para detectar a tiempo y apoyar mejores decisiones.`
Bajada: `Integramos trampas inteligentes, sensores, drones y conectividad 5G para generar un mapa de actividad de la broca y alertas tempranas.`

1. La broca del café: adulta perfora fruto, entra al grano y se reproduce. Foto grano perforado.
2. Trampa inteligente: con atrayente, cámara y Edge/IA que detecta y cuenta en tiempo real.
3. Sensores en la finca: temperatura, humedad, condiciones del cultivo. Texto: sensores IoT del campo ya tiene Reymond.
4. Dron (Raymond / Reymond): imágenes de la finca para complementar el monitoreo.
5. Conectividad 5G: conecta trampas, sensores y drones en tiempo real.
6. Edge + IA (en el nodo): identifica, cuenta y procesa en el borde. Procesamiento local, envía solo datos relevantes.
7. Mapa y alertas: plataforma con mapa de actividad, historial, alertas, recomendaciones. Mock mapa calor + móvil alerta `Aumento de actividad de broca en Zona 3`.

- Resultado para el productor (4): detecta a tiempo zonas con mayor actividad, prioriza inspección y manejo, menor pérdida de producción y mejor calidad del café, uso más eficiente de recursos.
- Escalable a futuro (3): otras plagas y cultivos, más trampas y fincas, integración con más datos agrícolas.

## Entidades / nombres propios detectados
- AgriVision / AgriVision (en IMG-1 aparece como `AgriVision`, probable typo por `AgriVision`).
- AgriVision 5G, AgriVision (landing usa AgriVision, imágenes usan AgriVision — alinear marca).
- Reymond / Raymond: aparece como `Raymond` (dron) y `Reymond` (dueño sensores campo). Verificar nombre correcto con el equipo.
- Hardware: Dragino (gateway LoRaWAN), Nokia FRRx502e, Nokia FRRO501c, Teltonika RUTX11, Nokia XR20.
- Atrayente: metanol + etanol.
- Plaga: broca del café (Coffee Berry Borer).

## Supuestos para refinar en ronda de preguntas
1. ¿Marca final: AgriVision vs AgriVision vs AgriVision? Landing dice AgriVision, imágenes dicen AgriVision + Plataforma AgriVision.
2. ¿Reymond es persona (productor / aliado con sensores y dron) o nombre del dron? Hay inconsistencia Raymond/Reymond.
3. ¿Gateway base para MVP y demo hackatón: Dragino + cuál de los 3 (FRRx502e / FRRO501c / RUTX11)?
4. ¿Nodo fauna (venado) es parte del MVP o visión futura? Solo aparece en IMG-1.
5. ¿Conectividad real en finca vs Testbed/Laboratorio para la demo del jurado?
6. Costos, energía (panel/batería) y mantenimiento de trampa: ¿datos reales o por estimar?
