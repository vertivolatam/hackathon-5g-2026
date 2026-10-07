<script setup>
import { ref, computed } from 'vue'
import { monitoreos, crearMonitoreo } from '../stores/monitoreos'
import { evidencias, crearEvidencia } from '../stores/evidencias'
import { visitas } from '../stores/visitas'

const props = defineProps({ email: { type: String, required: true } })

const misFincas = computed(() => {
  const nombres = visitas.filter((v) => v.tecnicoCorreo === props.email).map((v) => v.fincaNombre)
  return [...new Set(nombres)]
})

const misMonitoreos = computed(() => monitoreos.filter((m) => m.tecnicoEmail === props.email))
const misEvidencias = computed(() => evidencias.filter((e) => e.tecnicoEmail === props.email))

// --- Registrar monitoreos en campo ---
const monitoreo = ref({ finca: '', fecha: '', tipo: '', observaciones: '' })
const guardarMonitoreo = () => {
  crearMonitoreo({ ...monitoreo.value, tecnicoEmail: props.email })
  monitoreo.value = { finca: '', fecha: '', tipo: '', observaciones: '' }
}

// --- Subir evidencias de plagas ---
const evidencia = ref({ finca: '', plaga: '', severidad: null, fecha: '', descripcion: '', imagen: '' })
const imagenError = ref('')

const onImagen = (e) => {
  const archivo = e.target.files[0]
  if (!archivo) return
  if (!archivo.type.startsWith('image/')) {
    imagenError.value = 'El archivo debe ser una imagen.'
    return
  }
  imagenError.value = ''
  const reader = new FileReader()
  reader.onload = () => (evidencia.value.imagen = reader.result)
  reader.readAsDataURL(archivo)
}

const guardarEvidencia = () => {
  crearEvidencia({ ...evidencia.value, tecnicoEmail: props.email })
  evidencia.value = { finca: '', plaga: '', severidad: null, fecha: '', descripcion: '', imagen: '' }
}
</script>

<template>
  <section class="panel">
    <h2>Registrar monitoreos en campo</h2>
    <form class="form" @submit.prevent="guardarMonitoreo">
      <label>
        Finca
        <select v-model="monitoreo.finca" required>
          <option value="" disabled>Seleccione</option>
          <option v-for="f in misFincas" :key="f">{{ f }}</option>
        </select>
      </label>
      <label>Fecha <input v-model="monitoreo.fecha" type="date" required /></label>
      <label>
        Tipo de monitoreo
        <select v-model="monitoreo.tipo" required>
          <option value="" disabled>Seleccione</option>
          <option>Revisión de trampas</option>
          <option>Estado del cultivo</option>
          <option>Revisión de riego y sensores</option>
        </select>
      </label>
      <label>Observaciones <textarea v-model="monitoreo.observaciones" rows="3" required></textarea></label>
      <button type="submit" class="btn">Registrar</button>
    </form>

    <h3>Mis monitoreos</h3>
    <table class="tabla">
      <thead>
        <tr><th>Fecha</th><th>Finca</th><th>Tipo</th><th>Observaciones</th></tr>
      </thead>
      <tbody>
        <tr v-for="m in misMonitoreos" :key="m.id">
          <td>{{ m.fecha }}</td>
          <td>{{ m.finca }}</td>
          <td>{{ m.tipo }}</td>
          <td>{{ m.observaciones }}</td>
        </tr>
        <tr v-if="misMonitoreos.length === 0">
          <td colspan="4" class="vacio">Sin monitoreos registrados.</td>
        </tr>
      </tbody>
    </table>
  </section>

  <section class="panel">
    <h2>Subir evidencias de plagas</h2>
    <form class="form" @submit.prevent="guardarEvidencia">
      <label>
        Finca
        <select v-model="evidencia.finca" required>
          <option value="" disabled>Seleccione</option>
          <option v-for="f in misFincas" :key="f">{{ f }}</option>
        </select>
      </label>
      <label>Tipo de plaga/enfermedad <input v-model="evidencia.plaga" required /></label>
      <label>Severidad (%) <input v-model="evidencia.severidad" type="number" min="0" max="100" required /></label>
      <label>Fecha de detección <input v-model="evidencia.fecha" type="date" required /></label>
      <label>Descripción <textarea v-model="evidencia.descripcion" rows="3"></textarea></label>
      <label>Fotografía <input type="file" accept="image/*" @change="onImagen" /></label>
      <p v-if="imagenError" class="error">{{ imagenError }}</p>
      <img v-if="evidencia.imagen" :src="evidencia.imagen" class="preview" alt="evidencia" />
      <button type="submit" class="btn">Subir evidencia</button>
    </form>

    <h3>Mis evidencias</h3>
    <ul class="evidencias">
      <li v-for="e in misEvidencias" :key="e.id">
        <img v-if="e.imagen" :src="e.imagen" alt="evidencia" />
        <div>
          <strong>{{ e.plaga }}</strong> — {{ e.severidad }}% · {{ e.fecha }} · {{ e.finca }}
          <p>{{ e.descripcion }}</p>
        </div>
      </li>
      <li v-if="misEvidencias.length === 0" class="vacio">Sin evidencias subidas.</li>
    </ul>
  </section>
</template>

<style scoped>
.panel { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.panel h2 { font-family: 'DM Serif Display', serif; margin-bottom: 16px; }
.panel h3 { font-family: 'DM Serif Display', serif; margin: 16px 0 8px; }
.form { display: flex; flex-direction: column; gap: 12px; max-width: 480px; }
.form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 4px; }
.form input, .form select, .form textarea { border: 1px solid #ddd3c4; border-radius: 10px; padding: 8px 12px; font-size: 14px; font-family: 'Inter', sans-serif; }
.btn { background: #2D1B0E; color: #F7F5F0; border: none; border-radius: 999px; padding: 8px 18px; align-self: flex-start; }
.btn:hover { background: #52B788; }
.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.vacio { color: #8a7a6a; text-align: center; padding: 12px; }
.error { color: #c0392b; font-size: 13px; }
.preview { width: 120px; border-radius: 10px; }
.evidencias { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.evidencias li { display: flex; gap: 12px; background: #F7F5F0; border-radius: 12px; padding: 12px; font-size: 14px; }
.evidencias img { width: 80px; height: 80px; object-fit: cover; border-radius: 10px; }
.evidencias p { color: #8a7a6a; font-size: 13px; margin-top: 4px; }
</style>
