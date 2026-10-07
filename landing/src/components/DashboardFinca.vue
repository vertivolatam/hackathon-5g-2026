<script setup>
import { ref, computed, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import { obtenerLecturaFinca } from '../services/bioagroApi'

Chart.register(...registerables)

const props = defineProps({ finca: { type: Object, required: true } })
const emit = defineEmits(['volver'])

const emitVolver = () => emit('volver')

// RNF-04.2 — último dato disponible + indicación de fecha/hora de última actualización
const lectura = ref(props.finca.lecturaActual)
const ultimaActualizacion = ref(props.finca.lecturaActual?.fecha || null)
const errorApi = ref('')

onMounted(async () => {
  try {
    const res = await obtenerLecturaFinca(props.finca.id)
    lectura.value = res.lectura
    ultimaActualizacion.value = res.obtenidoEn
    if (res.origen === 'cache') {
      errorApi.value = `Sin conexión con la API de BioAgro. Mostrando el último dato disponible (${res.lectura.fecha}).`
    }
  } catch {
    errorApi.value = 'Sin conexión y sin datos en caché para esta finca.'
    lectura.value = null
  }
})

const iconosPrioridad = {
  Alta: '🔴',
  Seguimiento: '🟡',
  'Sin prioridad inmediata': '🟢',
}

// RF-04.4 — Filtros del historial
const filtroFecha = ref('')
const filtroTipo = ref('')

const tipos = computed(() => [...new Set(props.finca.detecciones.map((d) => d.tipo))])

const deteccionesFiltradas = computed(() =>
  props.finca.detecciones.filter(
    (d) =>
      (!filtroFecha.value || d.fecha === filtroFecha.value) &&
      (!filtroTipo.value || d.tipo === filtroTipo.value),
  ),
)

// Detecciones por período (para gráfico)
const deteccionesPorMes = computed(() => {
  const grupos = {}
  props.finca.detecciones.forEach((d) => {
    const mes = d.fecha.slice(0, 7)
    grupos[mes] = (grupos[mes] || 0) + 1
  })
  return Object.entries(grupos).sort()
})

const severidadCanvas = ref(null)
const sensoresCanvas = ref(null)
const deteccionesCanvas = ref(null)

onMounted(() => {
  new Chart(severidadCanvas.value, {
    type: 'line',
    data: {
      labels: props.finca.tendenciaSeveridad.map((t) => t.periodo),
      datasets: [{ label: 'Severidad (%)', data: props.finca.tendenciaSeveridad.map((t) => t.severidad), borderColor: '#c0392b', tension: 0.3 }],
    },
  })
  new Chart(sensoresCanvas.value, {
    type: 'bar',
    data: {
      labels: props.finca.actividadSensores.map((t) => t.periodo),
      datasets: [{ label: 'Sensores activos', data: props.finca.actividadSensores.map((t) => t.activos), backgroundColor: '#52B788' }],
    },
  })
  new Chart(deteccionesCanvas.value, {
    type: 'bar',
    data: {
      labels: deteccionesPorMes.value.map(([mes]) => mes),
      datasets: [{ label: 'Detecciones', data: deteccionesPorMes.value.map(([, n]) => n), backgroundColor: '#2D1B0E' }],
    },
  })
})
</script>

<template>
  <section class="dashboard">
    <button class="btn-link" @click="emitVolver">← Volver a fincas</button>
    <header class="dashboard__header">
      <h3>Dashboard — {{ finca.nombre }}</h3>
      <span class="prioridad">
        {{ iconosPrioridad[finca.prioridad] || '⚪' }} Prioridad: <strong>{{ finca.prioridad }}</strong>
      </span>
    </header>

    <p v-if="errorApi" class="alerta-api">{{ errorApi }}</p>

    <!-- RF-04.3 — Datos más recientes -->
    <div v-if="lectura" class="tarjetas">
      <div class="tarjeta">
        <span class="tarjeta__num">{{ lectura.temperatura }} °C</span>
        <span class="tarjeta__label">Temperatura · {{ lectura.fecha }}</span>
      </div>
      <div class="tarjeta">
        <span class="tarjeta__num">{{ lectura.humedad }} %</span>
        <span class="tarjeta__label">Humedad · {{ lectura.fecha }}</span>
      </div>
      <div v-for="p in lectura.plagas" :key="p.tipo" class="tarjeta">
        <span class="tarjeta__num">{{ p.severidad }} %</span>
        <span class="tarjeta__label">{{ p.tipo }} · severidad · {{ lectura.fecha }}</span>
      </div>
    </div>
    <p v-else class="vacio">Sin lecturas recientes de sensores.</p>
    <p v-if="ultimaActualizacion" class="ultima-act">Última actualización: {{ ultimaActualizacion }}</p>

    <!-- RF-04.4 — Historial con filtros -->
    <h4>Historial de detecciones</h4>
    <div class="filtros">
      <label>Fecha <input type="date" v-model="filtroFecha" /></label>
      <label>
        Tipo
        <select v-model="filtroTipo">
          <option value="">Todos</option>
          <option v-for="t in tipos" :key="t" :value="t">{{ t }}</option>
        </select>
      </label>
      <button class="btn-link" @click="filtroFecha = ''; filtroTipo = ''">Limpiar filtros</button>
    </div>
    <table class="tabla">
      <thead>
        <tr><th>Fecha</th><th>Tipo de incidencia</th><th>Severidad</th></tr>
      </thead>
      <tbody>
        <tr v-for="d in deteccionesFiltradas" :key="d.fecha + d.tipo">
          <td>{{ d.fecha }}</td>
          <td>{{ d.tipo }}</td>
          <td>{{ d.severidad }} %</td>
        </tr>
        <tr v-if="deteccionesFiltradas.length === 0">
          <td colspan="3" class="vacio">Sin resultados para los filtros aplicados.</td>
        </tr>
      </tbody>
    </table>

    <!-- RF-04.5 — Gráficos de tendencia -->
    <h4>Tendencias</h4>
    <div class="graficos">
      <div class="grafico"><canvas ref="severidadCanvas"></canvas></div>
      <div class="grafico"><canvas ref="sensoresCanvas"></canvas></div>
      <div class="grafico"><canvas ref="deteccionesCanvas"></canvas></div>
    </div>
  </section>
</template>

<style scoped>
.dashboard { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; display: flex; flex-direction: column; gap: 16px; }
.dashboard h3 { font-family: 'DM Serif Display', serif; }
.dashboard h4 { font-family: 'DM Serif Display', serif; margin-top: 8px; }
.dashboard__header { display: flex; justify-content: space-between; align-items: center; }
.prioridad { background: #F7F5F0; border-radius: 999px; padding: 6px 16px; font-size: 14px; }

.tarjetas { display: flex; gap: 16px; flex-wrap: wrap; }
.tarjeta { background: #F7F5F0; border-radius: 12px; padding: 16px 24px; display: flex; flex-direction: column; }
.tarjeta__num { font-size: 26px; font-weight: 600; color: #52B788; }
.tarjeta__label { font-size: 12px; color: #8a7a6a; }

.filtros { display: flex; gap: 16px; align-items: end; }
.filtros label { font-size: 12px; display: flex; flex-direction: column; gap: 4px; }
.filtros input, .filtros select { border: 1px solid #ddd3c4; border-radius: 8px; padding: 6px 10px; font-size: 13px; }

.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.vacio { color: #8a7a6a; text-align: center; padding: 12px; }

.alerta-api { background: #fff3cd; border-left: 4px solid #f39c12; border-radius: 8px; padding: 10px 14px; font-size: 13px; }
.ultima-act { font-size: 12px; color: #8a7a6a; }

.graficos { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grafico { background: #F7F5F0; border-radius: 12px; padding: 12px; }

.btn-link { background: none; border: none; color: #52B788; font-size: 13px; align-self: flex-start; }
</style>
