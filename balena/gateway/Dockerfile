FROM balenalib/raspberrypi4-64-debian:bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl xz-utils \
 && rm -rf /var/lib/apt/lists
# balenaCLI v25+ (docs.balena.io/reference/balena-cli/latest). Se instala
# en el host/CI, no en el device; esta imagen deja el runtime listo.
CMD ["sleep", "infinity"]
