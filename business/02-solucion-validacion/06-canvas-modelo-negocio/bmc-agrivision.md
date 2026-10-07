# BMC AgriVision — en limpio 7-oct-2026

Supersede a `00-bmc-indice.md` (borrador con marca vieja). Fuente: bitácora 5–7 oct + validación por espacios (`fase1..4-validacion.md`).
Leyenda: 🟢 validado · 🟡 parcial/hipótesis con señal · 🔴 hipótesis sin validar.

## 1. Problema 🟢 (matiz 🟡)

- 1240–4600 asociados por 4 técnicos: cobertura presencial imposible (Coopedota 4/5, ICAFE saturación en cosecha).
- Recomendaciones generales por falta de tiempo; fincas sin atención oportuna.
- Matiz: priorizar visitas duele donde hay presión; lo transversal es información oportuna.

## 2. Segmentos 🟢 perfiles / 🟡 conversión

- **Coops saturadas** (Coopedota): venden cobertura. 🟢
- **Instituciones escala** (ICAFE 24k): venden detección oportuna + dato histórico. 🟢
- **Coops con cobertura OK** (Coopetarrazu): venden anticipación de riesgo + integración de boletines. 🟢
- Usuarios: técnico (champion, 🟡 sin entrevistar); beneficiario: productor (🔴 sin entrevistar).

## 3. Propuesta de valor 🟡

- Paraguas: "datos del campo → señales oportunas: qué pasa, dónde mirar, cuándo actuar".
- Por segmento: priorizar visitas / alerta temprana a escala / riesgo + clima + boletines.
- NO es: diagnóstico automático, sustituto del técnico, trampa aislada, dependencia de dron/satélite.

## 4. Solución 🟡 (MVP técnico parcial)

- Nodo: trampa + cámara 13 MP (lente 8–12 mm close-up) + luz controlada + sensores si aportan.
- Edge AI → 5G SA → plataforma (integración, mapa, historial, prioridad) → validación del técnico → retroalimentación.
- Verificado: MQTT + API + topics en cluster; RF-DETR 0.2 s en PoC (sin clase broca aún). Pendiente: detección broca en campo, Edge en placa, óptica física.

## 5. Canales 🟡

- Venta: directo a cooperativa (piloto acompañado). Entrega de valor: WhatsApp/correo (pedido explícito). Marketing: landing + docs.

## 6. Relaciones 🟡

- Piloto con métrica previa; técnico valida en campo (<2 min/evento, hipótesis); el loop de validación mejora modelo y dataset.

## 7. Ingresos 🟡 hipótesis / 🔴 números

- Suscripción plataforma (coop) + instalación, mantenimiento, nodos, análisis avanzados.
- Primer precio real propuesto: piloto pagado con gate de resultados (fee reembolsable contra suscripción si cumple métrica).

## 8. Costos 🔴

- Nodo (cámara+lente+trampa+luz+energía), gateway prorrateado, conectividad, instalación/mantenimiento, validación campo, dev plataforma/IA. Primer dato real: capex del piloto 1–3 nodos.

## 9. Actividades clave 🟡

- Detección/conteo broca, calibración óptica + atrayente, pipeline Edge→5G→plataforma, mapa/alertas, integración clima/boletines, validación con técnicos.

## 10. Recursos clave 🟡

- Modelo + **dataset propio de campo** (moat), gateways, red 5G testbed, plataforma, contactos piloto. Equipo fundador: 🔴 sin definir.

## 11. Socios clave 🟡

- Coops piloto (ICAFE, Coopetarrazu interesadas; Coopedota dolor alto), ICAFE institucional, proveedores HW (cámara/lentes), Vertivo/Nokia (hackatón/5G).

## 12. Métricas 🟡

- Nodos activos, eventos/día, latencia captura→alerta, tiempo de validación del técnico, % adopción, precisión campo (meta honesta, no lab).

## 13. Impacto 🟡

- Menos insecticida preventivo, detección temprana → menos pérdida, mejor calidad, trazabilidad para certificación.

## 14. Ventaja injusta 🟡 (tesis, no activo aún)

- Loop técnico→historial→modelo con datos propios de campo + plataforma modular multi-cultivo. Se construye con cada piloto, no existe hoy.
