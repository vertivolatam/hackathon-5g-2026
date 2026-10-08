<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Chart, registerables } from 'chart.js'
import { cooperativas } from '../stores/cooperativas'
import { fincas } from '../stores/fincas'
import { visitas } from '../stores/visitas'
import { incidencias } from '../stores/boletin'
import { TILE_LAYER_URL, TILE_LAYER_ATTRIBUTION } from '../services/mapaService'

Chart.register(...registerables)

// ---------- RF-08.7 Filtros ----------
const filtroCoop = ref('')
const filtroRegion = ref('')
const filtroMes = ref('')

const regiones = computed(() => [...new Set(cooperativas.map((c) => c.region))])

const coopsFiltradas = computed(() =>
  cooperativas.filter(
    (c) => (!filtroCoop.value || c.id === filtroCoop.value) && (!filtroRegion.value || c.region === filtroRegion.value),
  ),
)
const coopIds = computed(() => new Set(coopsFiltradas.value.map((c) => c.id)))

const fincasFiltradas = computed(() => fincas.filter((f) => coopIds.value.has(f.cooperativaId)))
const visitasFiltradas = computed(() =>
  visitas.filter((v) => coopIds.value.has(v.cooperativaId) && (!filtroMes.value || v.fecha.startsWith(filtroMes.value))),
)
const incidenciasFiltradas = computed(() =>
  incidencias.filter((i) => !filtroMes.value || i.fecha.startsWith(filtroMes.value)),
)

// ---------- RF-08.1 Resumen global ----------
const alertasActivas = computed(() => incidenciasFiltradas.value.filter((i) => i.nivelRiesgo === 'Alta').length)

// ---------- RF-08.3 Incidencias ----------
const porTipo = computed(() => {
  const grupos = {}
  incidenciasFiltradas.value.forEach((i) => (grupos[i.tipo] = (grupos[i.tipo] || 0) + 1))
  return Object.entries(grupos)
})
const porUbicacion = computed(() => {
  const grupos = {}
  incidenciasFiltradas.value.forEach((i) => (grupos[i.finca] = (grupos[i.finca] || 0) + 1))
  return Object.entries(grupos)
})
const porMes = computed(() => {
  const grupos = {}
  incidenciasFiltradas.value.forEach((i) => {
    const mes = i.fecha.slice(0, 7)
    grupos[mes] = (grupos[mes] || 0) + 1
  })
  return Object.entries(grupos).sort()
})

// ---------- RF-08.4 Mitigación (mock) ----------
const mitigacion = computed(() => ({
  intervenidas: visitasFiltradas.value.filter((v) => v.estado === 'Completada').length,
  reincidencia: incidenciasFiltradas.value.filter((i) => i.nivelRiesgo === 'Alta').length,
  reduccion: ['May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct'].map((m, i) => ({ periodo: m, reduccion: [5, 12, 18, 25, 33, 41][i] })),
}))

// ---------- RF-08.5 Actividad técnica ----------
const visitasPorMes = computed(() => {
  const grupos = {}
  visitasFiltradas.value.forEach((v) => {
    const mes = v.fecha.slice(0, 7)
    grupos[mes] = (grupos[mes] || 0) + 1
  })
  return Object.entries(grupos).sort()
})
const visitasPorCoop = computed(() =>
  coopsFiltradas.value.map((c) => [c.nombre, visitasFiltradas.value.filter((v) => v.cooperativaId === c.id).length]),
)
const completitud = computed(() => {
  const total = visitasFiltradas.value.length || 1
  const completadas = visitasFiltradas.value.filter((v) => v.estado === 'Completada').length
  const canceladas = visitasFiltradas.value.filter((v) => v.estado === 'Cancelada').length
  return { completadas: Math.round((completadas / total) * 100), otras: Math.round(((total - completadas - canceladas) / total) * 100), canceladas: Math.round((canceladas / total) * 100) }
})

// ---------- RF-08.6 Sensores ----------
const sensoresPorCoop = computed(() =>
  coopsFiltradas.value.map((c) => {
    const sensores = fincas.filter((f) => f.cooperativaId === c.id).flatMap((f) => f.sensores)
    return [c.nombre, sensores.filter((s) => s.activo).length, sensores.filter((s) => !s.activo).length]
  }),
)

// ---------- RF-08.2 Mapa global ----------
const coloresRiesgo = { Alta: '#c0392b', Medio: '#f39c12', Bajo: '#52B788' }
const mapaEl = ref(null)
let mapa = null
let capa = null

const initMapa = () => {
  if (mapa) { mapa.remove(); mapa = null }
  mapa = L.map(mapaEl.value).setView([9.93, -84.09], 11)
  L.tileLayer(TILE_LAYER_URL, { attribution: TILE_LAYER_ATTRIBUTION }).addTo(mapa)
  capa = L.layerGroup().addTo(mapa)
  dibujar()
}

const dibujar = () => {
  if (!capa) return
  capa.clearLayers()
  fincasFiltradas.value.forEach((f) => {
    L.polygon(f.poligono, { color: coloresRiesgo[f.riesgo] || '#52B788' })
      .bindTooltip(`${f.nombre} — Riesgo: ${f.riesgo}`)
      .addTo(capa)
  })
}

// ---------- Gráficos ----------
const c1 = ref(null), c2 = ref(null), c3 = ref(null), c4 = ref(null), c5 = ref(null), c6 = ref(null), c7 = ref(null), c8 = ref(null), c9 = ref(null)
const cDet = ref(null), cTel = ref(null)
let charts = []

// Datos de telemetría/detecciones desde el backend (como Grafana)
const apiDetections = ref([])
const apiTelemetry = ref([])

const fetchGrafanaData = async () => {
  try {
    const d = await fetch(`${import.meta.env.VITE_API_BIOAGRO_URL}/api/detections?limit=50`).then(r => r.json())
    apiDetections.value = d.items || []
  } catch { apiDetections.value = [] }
  try {
    const t = await fetch(`${import.meta.env.VITE_API_BIOAGRO_URL}/api/telemetry?limit=50`).then(r => r.json())
    apiTelemetry.value = t.items || []
  } catch { apiTelemetry.value = [] }
}

const deteccionesPorHora = computed(() => {
  const grupos = {}
  apiDetections.value.forEach((d) => {
    const hora = (d.ts || '').slice(0, 13)
    if (hora) grupos[hora] = (grupos[hora] || 0) + 1
  })
  return Object.entries(grupos).sort()
})

const clasesDetectadas = computed(() => {
  const grupos = {}
  apiDetections.value.forEach((d) => {
    (d.detections || []).forEach((p) => {
      grupos[p.class] = (grupos[p.class] || 0) + 1
    })
  })
  return Object.entries(grupos).sort((a, b) => b[1] - a[1])
})

const telemetriaSerie = computed(() => {
  return apiTelemetry.value
    .map((t) => ({
      ts: (t.ts || '').slice(0, 16).replace('T', ' '),
      temperatura: t.payload?.temperatura ?? null,
      humedad: t.payload?.humedad ?? null,
    }))
    .reverse()
})

const crearCharts = () => {
  charts.forEach((c) => c.destroy())
  charts = []
  if (cDet.value) {
    charts.push(new Chart(cDet.value, {
      type: 'line',
      data: {
        labels: deteccionesPorHora.value.map(([h]) => h.slice(11) + ':00'),
        datasets: [{ label: 'Detecciones', data: deteccionesPorHora.value.map(([, n]) => n), borderColor: '#c0392b', tension: 0.3 }],
      },
    }))
  }
  if (cTel.value) {
    charts.push(new Chart(cTel.value, {
      type: 'line',
      data: {
        labels: telemetriaSerie.value.map((t) => t.ts.slice(11)),
        datasets: [
          { label: 'Temperatura (°C)', data: telemetriaSerie.value.map((t) => t.temperatura), borderColor: '#f39c12', tension: 0.3 },
          { label: 'Humedad (%)', data: telemetriaSerie.value.map((t) => t.humedad), borderColor: '#52B788', tension: 0.3 },
        ],
      },
    }))
  }
  charts.push(new Chart(c1.value, { type: 'bar', data: { labels: porTipo.value.map(([t]) => t), datasets: [{ label: 'Detecciones', data: porTipo.value.map(([, n]) => n), backgroundColor: '#c0392b' }] } }))
  charts.push(new Chart(c2.value, { type: 'bar', data: { labels: porUbicacion.value.map(([u]) => u), datasets: [{ label: 'Incidencias', data: porUbicacion.value.map(([, n]) => n), backgroundColor: '#f39c12' }] } }))
  charts.push(new Chart(c3.value, { type: 'line', data: { labels: porMes.value.map(([m]) => m), datasets: [{ label: 'Incidencias por mes', data: porMes.value.map(([, n]) => n), borderColor: '#c0392b', tension: 0.3 }] } }))
  charts.push(new Chart(c4.value, { type: 'bar', data: { labels: ['Intervenidas', 'Con reincidencia'], datasets: [{ label: 'Fincas', data: [mitigacion.value.intervenidas, mitigacion.value.reincidencia], backgroundColor: ['#52B788', '#c0392b'] }] } }))
  charts.push(new Chart(c5.value, { type: 'line', data: { labels: mitigacion.value.reduccion.map((r) => r.periodo), datasets: [{ label: 'Reducción severidad %', data: mitigacion.value.reduccion.map((r) => r.reduccion), borderColor: '#2d7a4f', tension: 0.3 }] } }))
  charts.push(new Chart(c6.value, { type: 'bar', data: { labels: visitasPorMes.value.map(([m]) => m), datasets: [{ label: 'Visitas', data: visitasPorMes.value.map(([, n]) => n), backgroundColor: '#2D1B0E' }] } }))
  charts.push(new Chart(c7.value, { type: 'doughnut', data: { labels: ['Completadas', 'En curso/Pendientes', 'Canceladas'], datasets: [{ data: [completitud.value.completadas, completitud.value.otras, completitud.value.canceladas], backgroundColor: ['#52B788', '#f39c12', '#c0392b'] }] } }))
  charts.push(new Chart(c8.value, { type: 'bar', data: { labels: sensoresPorCoop.value.map(([n]) => n), datasets: [{ label: 'Activos', data: sensoresPorCoop.value.map(([, a]) => a), backgroundColor: '#52B788' }, { label: 'Inactivos', data: sensoresPorCoop.value.map(([, , i]) => i), backgroundColor: '#c0392b' }] } }))
  charts.push(new Chart(c9.value, { type: 'bar', data: { labels: visitasPorCoop.value.map(([n]) => n), datasets: [{ label: 'Visitas por cooperativa', data: visitasPorCoop.value.map(([, v]) => v), backgroundColor: '#52B788' }] } }))
}

onMounted(() => nextTick(() => { initMapa(); fetchGrafanaData(); crearCharts() }))
watch([filtroCoop, filtroRegion, filtroMes, visitas, incidencias, fincas], () => nextTick(crearCharts), { deep: true })
watch([sensoresPorCoop, apiDetections, apiTelemetry], () => nextTick(crearCharts))
watch(fincasFiltradas, dibujar)
</script>

<template>
  <section class="admin">
    <h2>Dashboard global</h2>

    <div class="filtros">
      <label>
        Cooperativa
        <select v-model="filtroCoop">
          <option value="">Todas</option>
          <option v-for="c in cooperativas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
      </label>
      <label>
        Región
        <select v-model="filtroRegion">
          <option value="">Todas</option>
          <option v-for="r in regiones" :key="r">{{ r }}</option>
        </select>
      </label>
      <label>Período <input type="month" v-model="filtroMes" /></label>
      <button class="btn-link" @click="filtroCoop = ''; filtroRegion = ''; filtroMes = ''">Limpiar</button>
    </div>

    <!-- RF-08.1 -->
    <div class="tarjetas">
      <div class="tarjeta"><span class="tarjeta__num">{{ coopsFiltradas.filter(c => c.activa).length }}</span><span>Cooperativas activas</span></div>
      <div class="tarjeta"><span class="tarjeta__num">{{ fincasFiltradas.length }}</span><span>Fincas registradas</span></div>
      <div class="tarjeta"><span class="tarjeta__num">{{ visitasFiltradas.length }}</span><span>Visitas del período</span></div>
      <div class="tarjeta"><span class="tarjeta__num">{{ alertasActivas }}</span><span>Alertas activas</span></div>
    </div>

    <!-- RF-08.2 -->
    <h3>Mapa global de fincas y riesgo</h3>
    <div ref="mapaEl" class="mapa"></div>

    <!-- RF-08.3 -->
    <h3>Incidencias</h3>
    <div class="graficos">
      <div class="grafico"><canvas ref="c1"></canvas></div>
      <div class="grafico"><canvas ref="c2"></canvas></div>
      <div class="grafico"><canvas ref="c3"></canvas></div>
    </div>

    <!-- RF-08.4 -->
    <h3>Impacto de mitigación</h3>
    <div class="graficos graficos--2">
      <div class="grafico"><canvas ref="c4"></canvas></div>
      <div class="grafico"><canvas ref="c5"></canvas></div>
    </div>

    <!-- RF-08.5 -->
    <h3>Actividad técnica</h3>
    <div class="graficos">
      <div class="grafico"><canvas ref="c6"></canvas></div>
      <div class="grafico"><canvas ref="c9"></canvas></div>
      <div class="grafico">
        <p class="sub">Tasa de completitud de visitas</p>
        <canvas ref="c7"></canvas>
      </div>
    </div>

    <!-- RF-08.6 -->
    <h3>Métricas de sensores</h3>
    <div class="graficos graficos--2">
      <div class="grafico"><canvas ref="c8"></canvas></div>
    </div>

    <!-- Datos del backend en tiempo real (como Grafana) -->
    <h3>Detecciones y telemetría (API real)</h3>
    <div class="graficos graficos--2">
      <div class="grafico">
        <p class="sub">Detecciones por hora</p>
        <canvas ref="cDet"></canvas>
      </div>
      <div class="grafico">
        <p class="sub">Temperatura y humedad</p>
        <canvas ref="cTel"></canvas>
      </div>
    </div>
  </section>
</template>

<style scoped>
.admin { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; display: flex; flex-direction: column; gap: 16px; }
.admin h2 { font-family: 'DM Serif Display', serif; }
.admin h3 { font-family: 'DM Serif Display', serif; }
.filtros { display: flex; gap: 16px; align-items: end; }
.filtros label { font-size: 12px; display: flex; flex-direction: column; gap: 4px; }
.filtros select, .filtros input { border: 1px solid #ddd3c4; border-radius: 8px; padding: 6px 10px; font-size: 13px; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; }
.tarjetas { display: flex; gap: 16px; flex-wrap: wrap; }
.tarjeta { background: #F7F5F0; border-radius: 12px; padding: 16px 24px; display: flex; flex-direction: column; }
.tarjeta__num { font-size: 28px; font-weight: 600; color: #52B788; }
.mapa { height: 360px; border-radius: 12px; z-index: 0; }
.graficos { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.graficos--2 { grid-template-columns: repeat(2, 1fr); }
.grafico { background: #F7F5F0; border-radius: 12px; padding: 12px; }
.sub { font-size: 12px; color: #8a7a6a; margin-bottom: 8px; }
</style>
