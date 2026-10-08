# Incrustar Grafana en el landing

Guía según [el blog oficial de Grafana sobre incrustación](https://grafana.com/blog/how-to-embed-grafana-dashboards-into-web-applications/).
Aplica al Grafana del stack dev (`make dev-full`) y al de Minikube (`make mk-all`).

## Requisito: permitir el iframe

Por defecto Grafana rechaza cualquier `<iframe>` (protección anti-clickjacking).
Ya viene activado en ambos stacks:

- Compose: `GF_SECURITY_ALLOW_EMBEDDING=true` en `docker-compose.dev.yml`
- Minikube: `GF_SECURITY_ALLOW_EMBEDDING` en `backend/k8s/monitoring.yaml`

Sin esa variable el navegador bloquea el panel aunque la URL sea correcta.

## Opción usada aquí: auth anónima Viewer (solo dev)

El compose y el manifest crean Grafana con usuario anónimo de solo lectura,
así el iframe no pide login:

```yaml
GF_AUTH_ANONYMOUS_ENABLED: "true"
GF_AUTH_ANONYMOUS_ORG_ROLE: Viewer
```

> Producción: no exponer auth anónima. El blog recomienda snapshots
> (momento congelado, sin carga a los datasources), dashboards compartidos
> públicamente, o incrustación con autenticación detrás de un reverse proxy.

## Snippet del iframe

En **Share → Embed** Grafana genera la URL. El formato es:

```html
<iframe
  src="http://localhost:3000/d-solo/agrivision-detecciones/agrivision?orgId=1&panelId=1&theme=light&kiosk"
  width="100%" height="420" frameborder="0">
</iframe>
```

- `d-solo/...` renderiza un solo panel (sin chrome de Grafana).
- `?kiosk` oculta menús y cabecera.
- `theme=light|dark`, `refresh=15s` y `orgId=1` son opcionales.

El landing ya trae el componente `landing/src/components/GrafanaEmbed.vue`
que construye esa URL desde `VITE_GRAFANA_URL`, y la sección
`MonitoreoSection` lo muestra en la página principal. Sin `.env` configurado
muestra instrucciones en vez de un iframe roto. Ver `landing/.env.example`.

## Nota de cookies (`cookie_samesite`)

Con auth anónima no hay sesión que propagar, así que el valor por defecto
(`lax`) funciona. Si algún día se incrusta un dashboard **con login** desde
otro sitio, hay que revisar `cookie_samesite` y servir todo por HTTPS —
debilitarlo expone a CSRF (ver el blog).
