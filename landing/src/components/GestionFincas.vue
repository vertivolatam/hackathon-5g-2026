<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { fincas, crearFinca, actualizarFinca, eliminarFinca } from '../stores/fincas'
import DashboardFinca from './DashboardFinca.vue'
import { TILE_LAYER_URL, TILE_LAYER_ATTRIBUTION } from '../services/mapaService'

const props = defineProps({ cooperativaId: { type: String, required: true } })

const misFincas = computed(() => fincas.filter((f) => f.cooperativaId === props.cooperativaId))

const formularioVisible = ref(false)
const editandoId = ref(null)
const seleccionada = ref(null)
const dashboardFinca = ref(null)

const form = ref({ nombre: '', propietario: '', area: null, descripcion: '', poligonoTexto: '' })

// ---------- Mapa ----------
const mapaEl = ref(null)
let mapa = null
let capaFincas = null

const dibujarFincas = () => {
  if (!mapa) return
  capaFincas.clearLayers()
  misFincas.value.forEach((finca) => {
    const poligono = L.polygon(finca.poligono, { color: '#52B788' }).addTo(capaFincas)
    poligono.on('click', () => (seleccionada.value = finca))
    finca.sensores.forEach((s) => {
      L.circleMarker([s.lat, s.lng], {
        radius: 7,
        color: s.activo ? '#2d7a4f' : '#c0392b',
        fillColor: s.activo ? '#52B788' : '#e74c3c',
        fillOpacity: 0.9,
      })
        .bindTooltip(`${s.nombre} — ${s.activo ? 'Activo' : 'Inactivo'}`)
        .addTo(capaFincas)
    })
  })
}

const initMapa = () => {
  if (mapa) {
    mapa.remove()
    mapa = null
  }
  mapa = L.map(mapaEl.value).setView([9.9281, -84.0907], 13)
  L.tileLayer(TILE_LAYER_URL, { attribution: TILE_LAYER_ATTRIBUTION }).addTo(mapa)
  capaFincas = L.layerGroup().addTo(mapa)
  dibujarFincas()

  // RF-03.2 — Clic en el mapa agrega vértices al polígono en modo edición
  mapa.on('click', (e) => {
    if (!formularioVisible.value || !agregandoPuntos.value) return
    const coords = form.value.poligonoTexto
      ? form.value.poligonoTexto.split(';').map((p) => p.trim()).filter(Boolean)
      : []
    coords.push(`${e.latlng.lat.toFixed(5)},${e.latlng.lng.toFixed(5)}`)
    form.value.poligonoTexto = coords.join('; ')
  })
}

onMounted(initMapa)

// Al volver del dashboard, el div del mapa se recrea: reinicializar Leaflet
watch(dashboardFinca, (val) => {
  if (val === null) setTimeout(initMapa, 0)
})

watch(fincas, dibujarFincas, { deep: true })
watch(() => props.cooperativaId, dibujarFincas)

const agregandoPuntos = ref(false)

// ---------- CRUD ----------
const parsePoligono = (texto) =>
  texto
    .split(';')
    .map((p) => p.trim())
    .filter(Boolean)
    .map((p) => {
      const [lat, lng] = p.split(',').map(Number)
      return [lat, lng]
    })

const abrirCrear = () => {
  editandoId.value = null
  form.value = { nombre: '', propietario: '', area: null, descripcion: '', poligonoTexto: '' }
  formularioVisible.value = true
}

const abrirEditar = (finca) => {
  editandoId.value = finca.id
  form.value = {
    nombre: finca.nombre,
    propietario: finca.propietario,
    area: finca.area,
    descripcion: finca.descripcion,
    poligonoTexto: finca.poligono.map(([lat, lng]) => `${lat},${lng}`).join('; '),
  }
  formularioVisible.value = true
}

const guardar = () => {
  const datos = {
    nombre: form.value.nombre,
    propietario: form.value.propietario,
    area: Number(form.value.area),
    descripcion: form.value.descripcion,
    poligono: parsePoligono(form.value.poligonoTexto),
    cooperativaId: props.cooperativaId,
  }
  if (editandoId.value) actualizarFinca(editandoId.value, datos)
  else crearFinca(datos)
  formularioVisible.value = false
  agregandoPuntos.value = false
}

const eliminar = (finca) => {
  if (finca.visitasPendientes > 0) {
    alert(`¡Atención! "${finca.nombre}" tiene ${finca.visitasPendientes} visita(s) pendiente(s).`)
  }
  if (confirm(`¿Eliminar la finca "${finca.nombre}"?`)) {
    eliminarFinca(finca.id)
    if (seleccionada.value?.id === finca.id) seleccionada.value = null
  }
}

const sensoresActivos = (finca) => finca.sensores.filter((s) => s.activo).length
</script>

<template>
  <section class="fincas">
    <div class="fincas__header">
      <h2>Gestión de fincas</h2>
      <button class="btn" @click="abrirCrear">+ Nueva finca</button>
    </div>

    <!-- RF-04 — Dashboard de finca -->
    <DashboardFinca
      v-if="dashboardFinca"
      :finca="dashboardFinca"
      @volver="dashboardFinca = null"
    />

    <div v-else class="fincas__layout">
      <div ref="mapaEl" class="mapa"></div>

      <aside class="fincas__panel">
        <!-- Resumen al seleccionar (RF-03.7) -->
        <div v-if="seleccionada" class="resumen">
          <h3>{{ seleccionada.nombre }}</h3>
          <p><strong>Propietario:</strong> {{ seleccionada.propietario }} · <strong>Área:</strong> {{ seleccionada.area }} ha</p>
          <p><strong>Nivel de riesgo:</strong> {{ seleccionada.riesgo }}</p>
          <p><strong>Última alerta:</strong> {{ seleccionada.ultimaAlerta }}</p>
          <p><strong>Sensores activos:</strong> {{ sensoresActivos(seleccionada) }} / {{ seleccionada.sensores.length }}</p>
          <ul>
            <li v-for="s in seleccionada.sensores" :key="s.id">
              {{ s.nombre }} — {{ s.activo ? 'Activo' : 'Inactivo' }}
            </li>
          </ul>
          <div class="acciones">
            <button class="btn-mini" @click="abrirEditar(seleccionada)">Editar</button>
            <button class="btn-mini" @click="dashboardFinca = seleccionada">Dashboard</button>
            <button class="btn-mini btn-mini--danger" @click="eliminar(seleccionada)">Eliminar</button>
          </div>
        </div>

        <!-- Listado -->
        <ul v-else class="lista">
          <li v-for="f in misFincas" :key="f.id">
            <button class="lista__item" @click="seleccionada = f; mapa.flyTo(f.poligono[0], 15)">
              {{ f.nombre }} — {{ f.area }} ha
            </button>
            <button class="btn-mini" @click="abrirEditar(f)">Editar</button>
            <button class="btn-mini" @click="dashboardFinca = f">Dashboard</button>
            <button class="btn-mini btn-mini--danger" @click="eliminar(f)">Eliminar</button>
          </li>
          <li v-if="misFincas.length === 0" class="vacio">No hay fincas registradas.</li>
        </ul>
      </aside>
    </div>

    <!-- Formulario RF-03.1, RF-03.2, RF-03.5 -->
    <form v-if="formularioVisible" class="form" @submit.prevent="guardar">
      <h3>{{ editandoId ? 'Editar finca' : 'Registrar finca' }}</h3>
      <label>Nombre <input v-model="form.nombre" required /></label>
      <label>Propietario <input v-model="form.propietario" required /></label>
      <label>Área (ha) <input v-model="form.area" type="number" step="0.1" required /></label>
      <label>Descripción <textarea v-model="form.descripcion"></textarea></label>
      <label>
        Polígono (lat,lng; lat,lng; ...)
        <textarea v-model="form.poligonoTexto" rows="3" placeholder="9.9281,-84.0907; 9.931,-84.088; ..." required></textarea>
      </label>
      <label class="check">
        <input type="checkbox" v-model="agregandoPuntos" /> Trazar polígono haciendo clic en el mapa
      </label>
      <div class="form__acciones">
        <button type="submit" class="btn">Guardar</button>
        <button type="button" class="btn-link" @click="formularioVisible = false">Cancelar</button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.fincas { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.fincas__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.fincas__header h2 { font-family: 'DM Serif Display', serif; }
.fincas__layout { display: grid; grid-template-columns: 1fr 320px; gap: 16px; }
.mapa { height: 420px; border-radius: 12px; z-index: 0; }
.fincas__panel { font-size: 14px; }

.lista { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.lista li { display: flex; gap: 6px; align-items: center; }
.lista__item { flex: 1; text-align: left; background: #F7F5F0; border: none; border-radius: 8px; padding: 8px 12px; }
.lista__item:hover { background: #e9f5ee; }
.vacio { color: #8a7a6a; }

.resumen h3 { font-family: 'DM Serif Display', serif; margin-bottom: 8px; }
.resumen ul { margin: 8px 0 8px 20px; }
.acciones { display: flex; gap: 6px; margin-top: 10px; }

.btn { background: #2D1B0E; color: #F7F5F0; border: none; border-radius: 999px; padding: 8px 18px; }
.btn:hover { background: #52B788; }
.btn-mini { border: 1px solid #ddd3c4; background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 12px; }
.btn-mini:hover { border-color: #52B788; }
.btn-mini--danger:hover { border-color: #c0392b; color: #c0392b; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; }

.form { display: flex; flex-direction: column; gap: 12px; max-width: 560px; margin-top: 16px; }
.form h3 { font-family: 'DM Serif Display', serif; }
.form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 4px; }
.form input, .form textarea { border: 1px solid #ddd3c4; border-radius: 10px; padding: 8px 12px; font-size: 14px; font-family: 'Inter', sans-serif; }
.form__acciones { display: flex; gap: 12px; align-items: center; }
.check { flex-direction: row !important; align-items: center; font-weight: 400 !important; }
</style>
