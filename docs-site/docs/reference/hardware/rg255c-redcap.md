---
sidebar_position: 4
---

# RG255C RedCap (5G por trampa)

Ficha del módem para trampas con 5G propio. Fuente: [Quectel RG255C series](https://www.quectel.com/product/5g-redcap-rg255c-series/) · [especificación PDF M.2 V1.4](https://mc-technologies.com/wp-content/uploads/2026/07/Quectel_RG255C_Series_M.2_5G_Module_Specification_V1.4.pdf)

## Por qué RedCap y no el RM520N

RedCap (3GPP R17, 20 MHz, 1–2 antenas) es la radio 5G diseñada para IoT masivo: menos señalización y menos potencia que eMBB, con cobertura sub-6 completa. El RM520N-GL queda para el **backhaul del gateway**; el RG255C va **en cada trampa**.

> Requisito del hackatón: la guía de presentación exige capacidad 5G declarada (eMBB/URLLC/**mMTC**/slicing/edge) y su ejemplo es densidad de dispositivos ("1.000 sensores por km²" → mMTC; ver [mMTC como escenario](./mmtc-escenario)). La palabra "mMTC" no aparece en los PDF de Quectel (verificado por texto: 0 menciones en los 5 specs + manual AT); RedCap es la tecnología que la cubre en la práctica para este caso (sensores de bajo consumo a escala), frente al eMBB del RM520N que no escala en densidad ni en batería.

## Variantes y consumo (de la especificación)

| Variante | Forma | Alimentación | Sleep | Idle |
|---|---|---|---|---|
| RG255C-GL M.2 | M.2 Key B | 3.135–4.4V (típ. 3.7V) | ~2.8 mA | ~25 mA |
| RG255C-GL mini-PCIe | mini-PCIe 30×50.95 | 3.0–3.6V (típ. 3.3V) | ~3.6 mA | ~29–43 mA |

- Throughput: 223 Mbps DL / 123 Mbps UL (SA sub-6) + fallback LTE Cat 4.
- Interfaces: **USB 2.0 HS** (datos), UART ×2 (AT), I2C, SPI, PCIe 2.0, ADC, RESET_N, GPIOs.
- Antenas: celular ×2 + GNSS ×1; (U)SIM ×2; −40…+85 °C; GNSS multiconstelación opcional.
- Drivers USB: serial/RNDIS/QMI_WWAN/MBIM en Linux (el P4 en ESP-IDF levanta ECM por USB-OTG; en MicroPython solo plano AT).

## NB-IoT / LTE-M: no aplica (red privada)

- En los 6 PDF de Quectel (specs + manual AT): **0 menciones** de NB-IoT/LTE-M/Cat-M/eMTC.
- La guía del hackatón menciona LTE-M una vez como fallback 4G donde no hay 5G; con NPN privada ese párrafo no aplica: no hay red comercial a la cual caer.
- Fallback dentro de la NPN: **LTE Cat 4** (que el RG255C trae) solo si el core privado lo soporta; si la NPN es NR-only, el diseño es NR con PSM/eDRX y store-and-forward en la trampa ante huecos de cobertura del RAN propio.

## Integración con la trampa

- El P4 habla AT por UART (`apps/esp-32/drivers/modem.py`: registro C5GREG/CEREG, CSQ, PDP con APN por entorno).
- Datos: USB-OTG del P4 como host ECM en ESP-IDF; en MicroPython, `AT+QMT*` del módem (según firmware) o PPP.
- Energía: rail 3.7V propio con load-switch (ver `drivers/power.py`); el módem vive **apagado** fuera de la ventana de wake.
- MIPI intacta: la potencia solo gatea rieles; CSI-2 2-lane + SCCB sin cambios.
