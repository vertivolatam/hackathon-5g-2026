---
sidebar_position: 1
---

# Exponer con túnel Cloudflare

Quick Tunnels (sin cuenta, solo demo): la red bloquea UDP/QUIC, así que siempre con `--protocol http2`.

```bash
export PATH="$HOME/.local/bin:$PATH"
# Landing (landing/dist servido en 8000) y API (port-forward en 8001):
cloudflared tunnel --protocol http2 --url http://localhost:8000 &
cloudflared tunnel --protocol http2 --url http://localhost:8001 &
```

Cada túnel imprime su URL `*.trycloudflare.com`. Son efímeras: cambian en cada reinicio. Para producción, usar Named Tunnel con cuenta Cloudflare.
