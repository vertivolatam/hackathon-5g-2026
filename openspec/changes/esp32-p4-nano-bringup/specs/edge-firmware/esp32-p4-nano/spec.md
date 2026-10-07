# edge-firmware/esp32-p4-nano

Nodo de campo ESP32-P4-NANO en MicroPython: bring-up verificable de buses y periféricos de la placa (Waveshare ESP32-P4-NANO / WIFI6-DB) antes del pipeline de visión, más telemetría MQTT. (Migrado de Rust no_std: ver commit feat-esp32 breaking en PR #2.)

## ADDED Requirements

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

- WHEN corre el CI (`py_compile` + `tests/test_smoke.py` con I2C falso)
- THEN la verificación SHALL terminar sin errores y sin target RISC-V.
