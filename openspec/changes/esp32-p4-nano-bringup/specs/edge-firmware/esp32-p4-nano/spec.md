# edge-firmware/esp32-p4-nano

Nodo de campo ESP32-P4-NANO: bring-up verificable de buses y periféricos de la placa (Waveshare ESP32-P4-NANO / WIFI6-DB) antes del pipeline de visión.

## ADDED Requirements

### Requirement: Bus I2C compartido operativo

El firmware SHALL exponer un único bus I2C maestro a 400 kHz en SDA=GPIO7 y SCL=GPIO8, compartido entre todos los drivers sin tomar `&mut` por método (partición vía bus-sharing).

#### Scenario: Arranque con bus sano

- WHEN el nodo arranca con los periféricos conectados
- THEN el log de arranque SHALL reportar el bus I2C inicializado a 400 kHz en GPIO7/8 sin panic.

### Requirement: Retroiluminación del display 10.1"

El firmware SHALL fijar el brillo del panel escribiendo el registro `0x96` del controlador en la dirección 7-bit `0x45`.

#### Scenario: Brillo al 80% en arranque

- WHEN el nodo completa el bring-up con el display conectado
- THEN el log SHALL reportar `backlight ok` y el panel SHALL mostrar retroiluminación.

#### Scenario: Display desconectado

- WHEN el controlador `0x45` no hace ACK
- THEN el firmware SHALL reportar el NACK, SHALL continuar con el resto del bring-up y SHALL NOT hacer panic.

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

### Requirement: Display DSI nativo tras feature dedicada

Con `--features dsi`, el firmware SHALL construir el bus DSI con 2 lanes a 500 Mbps por defecto y SHALL exponer constructores de `DpiConfig` (800×1280 RGB565) y `Config` consistentes con `esp-hal::mipi_dsi`. La secuencia DCS del panel (JD9365/ILI9881C/EK79007) SHALL documentarse como portada del componente Waveshare ESP-IDF.

#### Scenario: Compilación con DSI

- WHEN se compila con `--features dsi` para `riscv32imafc-unknown-none-elf`
- THEN la compilación SHALL terminar sin errores.
