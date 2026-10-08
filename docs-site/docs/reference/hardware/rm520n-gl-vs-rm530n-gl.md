---
sidebar_position: 2
---

# RM520N-GL vs RM530N-GL (gateway 5G)

Ficha comparativa. Fuentes: [wiki RM520N-GL](https://www.waveshare.com/wiki/RM520N-GL) · [wiki RM530N-GL](https://www.waveshare.com/wiki/RM530N-GL)

## Común a ambos

- Quectel Snapdragon **X62**, 3GPP **Release 16**, NSA + SA, M.2 Key B 30×52 mm.
- GNSS multiconstelación (GPS/GLONASS/BDS/Galileo; antena en **ANT3**).
- Carrier: HAT USB 3.0 para Raspberry Pi (Raspberry Pi OS reciente lo levanta **sin drivers**, modo MBIM).
- Dial-up por AT: `AT+QCFG="usbnet",2` (MBIM recomendado) + `AT+CGDCONT=1,"IPV4V6","<APN>"`.

## Diferencias

| | RM520N-GL | RM530N-GL |
|---|---|---|
| 5G | Sub-6 | Sub-6 **+ mmWave** (n257/258/260/261) |
| Sub-6 SA | DL 4.2 Gbps | DL 2.4 Gbps |
| Certificaciones US | Verizon/AT&T **sí** | **no** |
| Precio | menor | mayor |

## Decisión: RM520N-GL

Costa Rica es sub-6 sin mmWave; el RM530N paga de más por bandas inutilizables y pierde certificaciones de operadores americanos. El propio wiki lo recomienda así.

## Notas de campo (del wiki, aplican al gateway)

- **Energía**: el módulo exige picos que el USB del Pi no sostiene → reinicios. Usar alimentación externa **5V/3A** al HAT (switch en EXT PWR) y cable USB doble si hace falta.
- Las 4 antenas van siempre conectadas; posicionamiento GNSS a 1 Hz máx (`AT+QGPS=1`, `AT+QGPSLOC=0`).
- Diagnóstico sin red: `AT+CPIN?`, `AT+COPS?`, `AT+QENG="servingcell"`, `AT+C5GREG?`.
- El HAT expone la red al Pi como interfaz USB; el `agent.py` del gateway no cambia (sigue publicando MQTT y `POST /api/detect`).
