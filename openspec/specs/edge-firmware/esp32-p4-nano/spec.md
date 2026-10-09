# edge-firmware/esp32-p4-nano Specification

## Purpose

Nodo de campo ESP32-P4-NANO en MicroPython: bring-up verificable de buses y periféricos de la placa (Waveshare ESP32-P4-NANO / WIFI6-DB) antes del pipeline de visión, más telemetría MQTT. (Migrado de Rust no_std: ver commit feat-esp32 breaking en PR #2.)

## Requirements

### Requirement: Bus I2C compartido operativo

El firmware SHALL exponer un único bus I2C maestro a 400 kHz en SDA=GPIO7 y SCL=GPIO8, compartido entre todos los drivers sin que ninguno lo cierre ni lo reconfigure.

#### Scenario: Arranque con bus sano

- WHEN el nodo arranca con los periféricos conectados
- THEN el log de arranque SHALL reportar el bus I2C inicializado a 400 kHz en GPIO7/8 y el nodo SHALL seguir al bring-up sin reiniciarse.

### Requirement: Retroiluminación del display 10.1"

El firmware SHALL fijar el brillo del panel escribiendo el registro `0x96` del controlador en la dirección 7-bit `0x45`.

#### Scenario: Brillo al 80% en arranque

- WHEN el nodo completa el bring-up con el display conectado
- THEN el log SHALL reportar `backlight ok` y el panel SHALL mostrar retroiluminación.

#### Scenario: Display desconectado

- WHEN el controlador `0x45` no hace ACK
- THEN el firmware SHALL reportar el NACK, SHALL continuar con el resto del bring-up y SHALL NOT detener el loop.

### Requirement: Táctil GT911 por polling

El firmware SHALL detectar el controlador táctil probando `0x5D` y luego `0x14`, y SHALL polear el primer punto de contacto limpiando el flag de buffer tras cada lectura. RST/INT no están ruteados y SHALL NOT requerirse.

#### Scenario: Touch presente

- WHEN alguna de las dos direcciones hace ACK
- THEN el log SHALL reportar la dirección en uso y los toques SHALL aparecer como `touch x=<..> y=<..>`.

#### Scenario: Touch ausente

- WHEN ninguna dirección hace ACK
- THEN el firmware SHALL reportar el NACK y SHALL seguir operando sin táctil.

### Requirement: Sanity de audio y cámara por probe

El firmware SHALL leer el CHIP_ID del codec ES8311 (`0x18`, reg `0xFD`) y SHALL probar las direcciones SCCB candidatas (`0x36`, `0x30`, `0x3C`) reportando el resultado sin bloquear el arranque si no hay ACK.

#### Scenario: Codec presente

- WHEN el ES8311 responde en `0x18`
- THEN el log SHALL mostrar su `chip_id`.

#### Scenario: Sin módulo de cámara

- WHEN ninguna dirección SCCB hace ACK
- THEN el log SHALL indicarlo y el nodo SHALL seguir en el loop de monitoreo.

### Requirement: Display DSI nativo por ESP-IDF

El display DSI serie 2-lane (800×1280) SHALL quedar fuera del firmware MicroPython: no existe driver DSI en MicroPython 2026. El firmware SHALL conservar los parámetros del panel (timings, lanes, bitrate) como contrato en `drivers/display.py` y SHALL documentar el camino de producción ESP-IDF + componente Waveshare. NINGÚN feature flag de compilación SHALL requerirse para el bring-up base.

#### Scenario: CI sin toolchain Rust

- WHEN corre el CI (`py_compile` + `tests/test_smoke.py` + `tests/test_dispenser.py` con I2C falso)
- THEN la verificación SHALL terminar sin errores y sin target RISC-V.

### Requirement: Cámara real (OV5647 PoC / AR1335 final)

El firmware SHALL probar presencia SCCB en `0x36/0x30/0x3C` (cubre OV5647 del KIT-C y AR1335 vía adaptador) y SHALL NOT intentar captura: sin driver CSI en MicroPython 2026. El contrato SHALL documentar que el CSI del P4 es de 2 lanes y que el kit EVK de la AR1335 usa conector de 70 pines (requiere adaptador FPC, no conexión directa).

#### Scenario: AR1335 montada vía adaptador

- WHEN el sensor hace ACK en una dirección candidata
- THEN el log SHALL reportar la dirección y el nodo SHALL seguir en telemetría (la captura real es ESP-IDF `esp_video`).

#### Scenario: Sin cámara (bring-up pelado)

- WHEN ninguna dirección SCCB hace ACK
- THEN el log SHALL indicarlo y el bring-up SHALL completarse igual.

### Requirement: 5G propio por trampa (RedCap + potencia)

La trampa con 5G propio SHALL llevar módem Quectel RG255C (RedCap R17, no eMBB) con rail conmutado por load-switch, y SHALL operar en duty-cycle: módem y cámara apagados fuera de la ventana de wake. El firmware SHALL registrar por AT (C5GREG/CEREG), levantar PDP con APN de entorno y publicar; si no hay registro, SHALL apagar el módem y seguir en local. El wake SHALL desfasarse por `trap_id` para no registrar el enjambre a la vez.

#### Scenario: Ventana de wake con cobertura

- WHEN el módem responde AT, registra (stat 1/5) y el PDP sube
- THEN el nodo SHALL publicar telemetría y SHALL apagar módem y cámara al cerrar la ventana.

#### Scenario: Sin cobertura

- WHEN el registro no llega en los reintentos
- THEN el nodo SHALL apagar el módem, SHALL NOT bloquear el loop y SHALL reintentar en el siguiente ciclo.

### Requirement: MIPI de cámara intacta ante el rediseño de potencia

El rediseño de potencia SHALL limitarse a gatear rieles: CSI-2 2-lane, bus SCCB en GPIO7/8, direcciones de probe y timings SHALL NOT cambiar. `drivers/camera.py` SHALL seguir pasando su smoke sin modificaciones de protocolo.

#### Scenario: Revisión de placa de potencia

- WHEN se cambia la placa de potencia (nuevos load-switches o GPIOs)
- THEN solo `board.py` (sección POWER) SHALL cambiar; ningún driver CSI/SCCB SHALL requerir cambios.

### Requirement: Dosificación de atrayente por EZO-PMP

#### Scenario: Dosis diurna y acumulación nocturna

- WHEN son las 13:00 (1.0 ml/h) con depósito suficiente
- THEN la bomba SHALL recibir `D,1.00` y el depósito estimado SHALL descontar 1.0 ml.
- WHEN son tres horas seguidas de 0.2 ml/h
- THEN al tercer tick SHALL dosificar 0.6 ml acumulados, ni antes ni dos veces la misma hora.

#### Scenario: Sin hora real o sin bomba

- WHEN el RTC/NTP no da año válido o la EZO-PMP no hace ACK en 0x67
- THEN el firmware SHALL NOT dosificar y SHALL seguir en telemetría (fail-safe).

### Requirement: Luz ambiental e iluminación nocturna

La trampa SHALL medir lux con BH1750 por I2C (0x23, bus compartido, sin cerrar ni reconfigurar) y SHALL encender el iluminador nocturno (GPIO por MOSFET) cuando lux < `LUX_NIGHT_THRESHOLD`, para seguir capturando broca de noche. De día SHALL apagarlo (~3W de ahorro). La telemetría SHALL incluir `lux` y `night_light`. Sin año RTC/NTP válido o sin ACK del sensor, SHALL conservar el último estado y seguir operando.

#### Scenario: Anochece en campo

- WHEN el BH1750 lee < 10 lx y el iluminador está apagado
- THEN el firmware SHALL encenderlo, SHALL reportar `night_light=true` y la siguiente captura SHALL salir iluminada.

#### Scenario: Sensor ausente

- WHEN el BH1750 no hace ACK en 0x23
- THEN el bring-up SHALL reportar el NACK, SHALL NOT bloquearse y el iluminador SHALL quedar en su último estado por defecto apagado al arranque.

## Referencias

- <https://www.waveshare.com/esp32-p4-nano.htm>
- <https://docs.waveshare.com/ESP32-P4-NANO>
- <https://www.technexion.com/shop/embedded-vision/mipi-csi2/evk/70-pin/tevm-ar1335-c-s85-ir-evk/>
- <https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf>
- <https://atlas-scientific.com/peristaltic/ezo-pmp/>
- <https://files.atlas-scientific.com/EZO_PMP_Datasheet.pdf>
- <https://www.adafruit.com/product/4681>
- <https://www.quectel.com/product/5g-redcap-rg255c-series/>
- <https://mc-technologies.com/wp-content/uploads/2026/07/Quectel_RG255C_Series_M.2_5G_Module_Specification_V1.4.pdf>
