<!-- Incrustación de un panel Grafana por <iframe>, según
  https://grafana.com/blog/how-to-embed-grafana-dashboards-into-web-applications/
  Requiere en Grafana: GF_SECURITY_ALLOW_EMBEDDING=true (ver docker-compose.dev.yml
  y backend/k8s/monitoring.yaml). Con auth anónima Viewer el iframe no pide login.
  Usa la URL d-solo con ?kiosk para mostrar solo el panel, sin chrome de Grafana.
-->
<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    dashboardUid?: string
    panelId?: number
    theme?: 'light' | 'dark'
    refresh?: string
    title?: string
  }>(),
  {
    dashboardUid: 'agrivision-detecciones',
    panelId: 1,
    theme: 'light',
    refresh: '15s',
    title: 'Grafana',
  },
)

const baseUrl = (import.meta.env.VITE_GRAFANA_URL as string | undefined)?.replace(/\/$/, '')
const uid = (import.meta.env.VITE_GRAFANA_DASHBOARD_UID as string | undefined) || props.dashboardUid

const src = computed(() =>
  baseUrl
    ? `${baseUrl}/d-solo/${uid}/agrivision?orgId=1&panelId=${props.panelId}&theme=${props.theme}&refresh=${props.refresh}&kiosk`
    : '',
)
</script>

<template>
  <div class="grafana-embed">
    <iframe
      v-if="src"
      :src="src"
      :title="title"
      loading="lazy"
      referrerpolicy="no-referrer"
    />
    <p v-else class="grafana-embed__fallback">
      Define <code>VITE_GRAFANA_URL</code> en <code>landing/.env</code> para ver el panel en vivo
      (ver <code>landing/.env.example</code>). Con <code>make dev-full</code> Grafana queda en
      <code>http://localhost:3000</code> (o en <code>$GRAFANA_PORT</code> si el 3000 está ocupado).
    </p>
  </div>
</template>

<style scoped>
.grafana-embed iframe {
  width: 100%;
  height: 420px;
  border: 1px solid #e8e4dd;
  border-radius: 4px;
  background: white;
}
.grafana-embed__fallback {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #4a5568;
  background: white;
  border: 1px dashed #c9c3b8;
  border-radius: 4px;
  padding: 2rem;
  text-align: center;
}
</style>
