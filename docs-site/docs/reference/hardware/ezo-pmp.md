---
sidebar_position: 6
---

# EZO-PMP (bomba de atrayente)

Ficha de la bomba peristáltica de la trampa. Fuentes: [atlas-scientific.com/peristaltic/ezo-pmp](https://atlas-scientific.com/peristaltic/ezo-pmp/) · [datasheet V3.0 (PDF)](https://files.atlas-scientific.com/EZO_PMP_Datasheet.pdf)

## Por qué esta bomba

Dosifica por **volumen nativo** (±1%, mínimo 0.5 ml): el firmware ordena `D,<ml>` y la bomba cuenta sola. Sin temporizar GPIOs ni calibrar caudal por bomba — crítico a 1.000 trampas.

## Datos duros

- Protocolo **I2C (default 0x67)** + UART, ASCII. Comparte el bus GPIO7/8 del P4 (sin choque: 0x45/0x5D/0x14/0x18/0x36 ya ocupadas, 0x67 libre).
- Comandos: `D,[ml]` dosifica · `D,?` estado (`?D,<vol>,<pumping>`) · `X` para · `Tv,?` total acumulado · `Sleep` bajo consumo · `Cal,[ml]` calibración de 1 punto.
- I2C: escribir comando → esperar **300 ms** → leer (byte0 = 1 ok / 2 fallo / 254 pendiente / 255 sin datos).
- Caudal 0.5–105 ml/min, tubo 5 mm O.D., cabezal 8.1 m, food-safe.
- **Lógica 3.3–5V, MOTOR 12–24V**: la placa de potencia SHALL llevar riel de 12V dedicado (el resto del nodo es 3.3/5V).
- ~$95 c/u (menos por volumen); driver en `apps/esp-32/drivers/dispenser.py`, tabla horaria en `config.py`.

## Implicación de diseño

La tabla horaria baja de 0.5 ml/h de noche: el driver **acumula** hasta juntar el mínimo dispensable. Sin hora real (NTP/RTC) no dosifica (fail-safe). El nivel del depósito es estimado por software y viaja en la telemetría (`cebo_ml`, `cebo_low`).
