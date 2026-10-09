---
sidebar_position: 5
---

# Validar el enlace 5G (confiabilidad)

Cómo se demuestra que la conectividad 5G de cada trampa es confiable: qué se mide, dónde se ve y qué criterio acepta.

## Capas de evidencia (todas existen)

| # | Capa | Qué demuestra | Dónde se ve |
|---|---|---|---|
| 1 | Registro y señal en la trampa | El RG255C se registra (C5GREG/CEREG) y reporta CSQ→dBm (`drivers/modem.py`) | Serie en campo; `rssi_dbm` en telemetría |
| 2 | Telemetría con RSSI | Cada publish lleva `rssi_dbm`; huecos = trampa o enlace caído | `GET /api/telemetry`, Postgres |
| 3 | Métricas Prometheus | `agrivision_mqtt_connected`, `agrivision_trap_rssi_dbm{trap_id}`, `agrivision_telemetry_ingested_total` | `/metrics`, dashboard MQTT |
| 4 | Dashboard | RSSI por trampa en el tiempo + clientes/throughput del broker | Grafana "AgriVision — MQTT" |
| 5 | Fail-safe en firmware | Sin registro no hay gasto de energía ni cuelgue: `wait_registered` con reintentos, módem OFF, reintento al siguiente ciclo | `drivers/modem.py`, `main.py` |
| 6 | Store-and-forward | Sin PDP la trampa sigue en local y reintenta (nunca pierde el ciclo por red) | `main.py` (best-effort) |

## Procedimiento en finca (por trampa, al instalar)

```bash
# 1. Registro y señal (serie de la trampa o AT por USB)
AT+C5GREG?        # esperar ,1 o ,5
AT+CSQ            # >= 15 usable, >= 20 bueno  (-113+2*rssi dBm)
AT+QENG="servingcell"   # celda + banda de la NPN
# 2. Datos: ping al core + POST /api/fotos de prueba
# 3. Soak 24 h: telemetría cada 15 min sin huecos en Grafana
```

## Criterios de aceptación (piloto)

- Attach al primer intento ≥ 95% (reintentos acotados por `wait_registered`).
- RSSI ≥ -95 dBm en el punto de instalación (reubicar trampa/antena si no).
- 0 huecos de telemetría en soak de 24 h (un hueco = wake perdido → revisar energía antes que red).
- Foto de prueba visible en el dashboard de Fotos de punta a punta.
