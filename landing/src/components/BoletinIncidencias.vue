<script setup>
import { ref, computed, onMounted } from 'vue'
import { incidencias, distanciaKm } from '../stores/boletin'
import { fincas } from '../stores/fincas'
import { notificaciones } from '../stores/notificaciones'
import { enviarCorreo } from '../services/correoService'

const props = defineProps({ cooperativaId: { type: String, required: true } })

const misFincas = computed(() => fincas.filter((f) => f.cooperativaId === props.cooperativaId))

// RF-07.3 — proximidad a la finca más cercana de la cooperativa
const proximidad = (inc) => {
  let min = Infinity
  misFincas.value.forEach((f) => {
    f.poligono.forEach(([lat, lng]) => {
      min = Math.min(min, distanciaKm(inc.lat, inc.lng, lat, lng))
    })
  })
  return min
}

const clasificar = (km) => (km < 1 ? 'Muy cercana' : km < 3 ? 'Cercana' : km < 8 ? 'Media' : 'Lejana')

const ordenadas = computed(() =>
  [...incidencias]
    .map((i) => ({ ...i, distancia: proximidad(i) }))
    .sort((a, b) => a.distancia - b.distancia),
)

// RF-07.5 — filtros del historial
const filtroFecha = ref('')
const filtroTipo = ref('')
const filtroRiesgo = ref('')

const tipos = computed(() => [...new Set(incidencias.map((i) => i.tipo))])

const filtradas = computed(() =>
  ordenadas.value.filter(
    (i) =>
      (!filtroFecha.value || i.fecha === filtroFecha.value) &&
      (!filtroTipo.value || i.tipo === filtroTipo.value) &&
      (!filtroRiesgo.value || i.nivelRiesgo === filtroRiesgo.value),
  ),
)

const altas = computed(() => ordenadas.value.filter((i) => i.nivelRiesgo === 'Alta'))

// RF-07.4 — notificar incidencias de alta prioridad en la zona
onMounted(() => {
  altas.value.slice(0, 3).forEach((i) => {
    const yaNotificada = notificaciones.some((n) => n.asunto.includes(i.tipo + ' · ' + i.fecha))
    if (!yaNotificada) {
      enviarCorreo(
        'alertas@bioagro.cr',
        `⚠️ Alerta alta prioridad: ${i.tipo} · ${i.fecha}`,
        `Incidencia de riesgo alto reportada:\nTipo: ${i.tipo}\nSeveridad: ${i.severidad}%\nUbicación aprox: ${i.finca}\nFecha: ${i.fecha}`,
      )
    }
  })
})
</script>

<template>
  <section class="boletin">
    <h2>Boletín de incidencias de la región</h2>

    <div v-for="i in altas.slice(0, 2)" :key="i.id" class="alerta">
      ⚠️ Incidencia de <strong>alta prioridad</strong>: {{ i.tipo }} ({{ i.severidad }}%) detectada en {{ i.finca }} el {{ i.fecha }}.
    </div>

    <div class="filtros">
      <label>Fecha <input type="date" v-model="filtroFecha" /></label>
      <label>
        Tipo
        <select v-model="filtroTipo">
          <option value="">Todos</option>
          <option v-for="t in tipos" :key="t">{{ t }}</option>
        </select>
      </label>
      <label>
        Riesgo
        <select v-model="filtroRiesgo">
          <option value="">Todos</option>
          <option>Alta</option>
          <option>Media</option>
          <option>Baja</option>
        </select>
      </label>
      <button class="btn-link" @click="filtroFecha = ''; filtroTipo = ''; filtroRiesgo = ''">Limpiar</button>
    </div>

    <table class="tabla">
      <thead>
        <tr><th>Fecha</th><th>Tipo</th><th>Severidad</th><th>Riesgo</th><th>Ubicación aprox.</th><th>Proximidad</th></tr>
      </thead>
      <tbody>
        <tr v-for="i in filtradas" :key="i.id">
          <td>{{ i.fecha }}</td>
          <td>{{ i.tipo }}</td>
          <td>{{ i.severidad }} %</td>
          <td>
            <span class="badge" :class="'badge--' + i.nivelRiesgo">
              {{ i.nivelRiesgo === 'Alta' ? '🔴' : i.nivelRiesgo === 'Media' ? '🟡' : '🟢' }} {{ i.nivelRiesgo }}
            </span>
          </td>
          <td>{{ i.finca }} ({{ i.lat.toFixed(3) }}, {{ i.lng.toFixed(3) }})</td>
          <td>{{ clasificar(i.distancia) }} · {{ i.distancia.toFixed(1) }} km</td>
        </tr>
        <tr v-if="filtradas.length === 0">
          <td colspan="6" class="vacio">Sin incidencias para los filtros aplicados.</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.boletin { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.boletin h2 { font-family: 'DM Serif Display', serif; margin-bottom: 16px; }
.alerta { background: #fdecea; border-left: 4px solid #c0392b; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; font-size: 14px; }
.filtros { display: flex; gap: 16px; align-items: end; margin-bottom: 16px; }
.filtros label { font-size: 12px; display: flex; flex-direction: column; gap: 4px; }
.filtros input, .filtros select { border: 1px solid #ddd3c4; border-radius: 8px; padding: 6px 10px; font-size: 13px; }
.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; }
.badge--Alta { background: var(--color-prioridad-alta-bg); color: var(--color-prioridad-alta); }
.badge--Media { background: var(--color-prioridad-seguimiento-bg); color: var(--color-prioridad-seguimiento); }
.badge--Baja { background: var(--color-prioridad-ok-bg); color: var(--color-prioridad-ok); }
.vacio { text-align: center; color: #8a7a6a; padding: 12px; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; align-self: center; }
</style>
