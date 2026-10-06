# BMC en limpio — BioAgro 5G / BioTrap / RuralIA

Estado: BORRADOR para depurar por Fabiola — no validado.
Fuente: `business/00-fuentes-visuales/inferencia-imagenes.md` (4 imágenes Descargas/hackathons) + landing `bio-trap/` + `business/README.md`.
Modo: sale de simulación — draft PR sin mergear.

## 1. Problema (Problem)
- Broca del café perfora fruto y se reproduce en grano → pérdida de producción y calidad.
- Detección tardía, monitoreo manual, sin mapa de actividad en tiempo real.
- Exceso de insecticida por aplicación preventiva sin datos.

## 2. Segmento de Clientes (Customer Segments)
- Productores de café Costa Rica (finca con/sin sensores Reymond).
- Técnicos agrícolas + cooperativas (multi-finca).
- Hackatón: jurado Vertivo / Nokia (valida uso 5G Testbed/Laboratorio).

## 3. Propuesta de Valor (Value Proposition)
- Detectar broca a tiempo y apoyar mejores decisiones.
- Mapa de actividad + historial/tendencias + alertas tempranas + recomendaciones de manejo.
- Trampa autónoma solar + IA en borde (Edge AI — Edge Artificial Intelligence) que solo envía datos relevantes.

## 4. Solución (Solution)
- Trampa: panel solar, cámara + Edge AI, atrayente metanol + etanol, captura selectiva, batería, GPS (Global Positioning System).
- Sensores en finca: temperatura, humedad, condiciones del cultivo (IoT (Internet of Things) ya existente).
- Dron Raymond/Reymond: imágenes complementarias.
- Conectividad: LoRaWAN (Long Range Wide Area Network) 2–15 km → Gateway Dragino → Nokia FRRx502e (Interior) / FRRO501c (Exterior) / Teltonika RUTX11 → Red 5G → Servidor Edge/Nube → Plataforma RuralIA + Edge (Web/App) → Nokia XR20.
- Nodo 4 fauna (venado) solo visión, no MVP (Minimum Viable Product).

## 5. Canales (Channels)
- Directo en finca, cooperativas, técnicos.
- Landing BioTrap (`bio-trap/`) + demo hackatón.
- App Web/Móvil RuralIA.

## 6. Relación con Clientes (Customer Relationships)
- Alertas automáticas Zona 3, mapa Trampa 1 Baja / 2 Media / 3 Alta.
- Soporte técnico instalación trampa/gateway.
- Mejora continua del modelo IA.

## 7. Fuentes de Ingreso (Revenue Streams)
- A definir por Fabiola: [hardware trampa + suscripción plataforma / por trampa / por finca / cooperativa].
- Supuesto: MVP 1 trampa → red de trampas/fincas/regiones.

## 8. Estructura de Costos (Cost Structure)
- Hardware: trampa, Dragino, Nokia/Teltonika, XR20, panel/batería.
- Conectividad 5G/LoRa, nube/edge, desarrollo IA + plataforma.
- Instalación, mantenimiento, energía días nublados.

## 9. Actividades Clave (Key Activities)
- Conteo broca Edge AI, calibración atrayente, integración LoRa → 5G → Edge, mapa/alertas, integración clima/mapas.

## 10. Recursos Clave (Key Resources)
- Modelo IA broca, gateways, Red 5G Testbed, plataforma RuralIA, equipo campo + datos Reymond.

## 11. Socios Clave (Key Partners)
- Nokia (FRRx502e/FRRO501c/XR20), Dragino, Teltonika, Reymond (finca/sensores/dron), cooperativas, Vertivo hackatón.

## 12. Métricas Clave (Key Metrics)
- Trampas activas, % detección temprana, latencia LoRa → alerta, reducción pérdida/insecticida, actividad Zona 3.

## 13. Métricas de Impacto (Impact Metrics — IRIS+, Impact Reporting and Investment Standards)
- Productividad y sostenibilidad, menor insecticida, mejor calidad del café, uso eficiente de recursos.

## 14. Ventaja Injusta + Escalabilidad (Unfair Advantage)
- Edge AI + LoRaWAN + 5G integrado en campo real.
- Escalable: otras plagas/cultivos, más trampas/fincas, más datos agrícolas.

## Dudas para Fabiola depurar
1. Marca: BioAgro vs BioTrap vs RuralIA.
2. Raymond vs Reymond.
3. Gateway MVP para demo.
4. Nodo fauna ¿in/out?
5. Precio y costo real trampa.
6. Testbed vs finca real en demo.

---
Progreso: Fase 6/21 vista — Espacio 2 parcial. Fases 7–8 y Puerta 2 pendientes.
En flujo completo serían 15 archivos en `02-solucion-validacion/` + `15-entrevista-solucion.md` + `16-experimento-mvp.md`.
