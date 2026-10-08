FROM rust:bookworm
# espflash: flasheo ESP-IDF/factory del ESP32-P4-NANO por serie.
RUN cargo install espflash
# mpremote: copia del firmware MicroPython (apps/esp-32/) sin compilar.
#   mpremote connect /dev/ttyACM0 cp -r boot.py main.py config.py board.py drivers/ :
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
 && rm -rf /var/lib/apt/lists \
 && pip install --break-system-packages --no-cache-dir mpremote
WORKDIR /fw
CMD ["sleep", "infinity"]
