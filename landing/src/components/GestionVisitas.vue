<script setup>
import { ref, computed } from 'vue'
import { visitas, crearVisita, actualizarVisita, cancelarVisita } from '../stores/visitas'
import { fincas } from '../stores/fincas'
import { tecnicos } from '../stores/tecnicos'
import { notificaciones } from '../stores/notificaciones'
import { enviarCorreo } from '../services/correoService'

const props = defineProps({ cooperativaId: { type: String, required: true } })

const misVisitas = computed(() => visitas.filter((v) => v.cooperativaId === props.cooperativaId))
const misFincas = computed(() => fincas.filter((f) => f.cooperativaId === props.cooperativaId))
const misTecnicos = computed(() => tecnicos.filter((t) => t.cooperativaId === props.cooperativaId && t.activo))
const tareasPendientes = computed(() => misVisitas.value.filter((v) => v.recordatorioManualPendiente && v.estado !== 'Cancelada'))

const formularioVisible = ref(false)
const editandoId = ref(null)
const form = ref({ fincaId: '', tecnicoId: '', fecha: '', hora: '', motivo: '' })

const abrirCrear = () => {
  editandoId.value = null
  form.value = { fincaId: '', tecnicoId: '', fecha: '', hora: '', motivo: '' }
  formularioVisible.value = true
}

const abrirEditar = (v) => {
  editandoId.value = v.id
  form.value = { fincaId: v.fincaId, tecnicoId: v.tecnicoId, fecha: v.fecha, hora: v.hora, motivo: v.motivo }
  formularioVisible.value = true
}

const detalleCita = (finca, tecnico, fecha, hora, motivo) =>
  `Finca: ${finca.nombre}\nFecha: ${fecha}\nHora: ${hora}\nMotivo: ${motivo}\nTécnico: ${tecnico.nombre}`

const notificarCita = (finca, tecnico, propietarioCorreo, fecha, hora, motivo, cambio = false) => {
  const asunto = cambio ? 'Actualización de visita técnica — BioAgro' : 'Nueva visita técnica agendada — BioAgro'
  const cuerpo = `${cambio ? 'La visita ha sido modificada.' : 'Se ha agendado una visita.'}\n\n${detalleCita(finca, tecnico, fecha, hora, motivo)}`
  enviarCorreo(tecnico.correo, asunto, cuerpo)
  enviarCorreo(propietarioCorreo, asunto, cuerpo)
}

const guardar = () => {
  const finca = misFincas.value.find((f) => f.id === form.value.fincaId)
  const tecnico = misTecnicos.value.find((t) => t.id === form.value.tecnicoId)
  const propietarioCorreo = 'propietario@example.com'

  if (editandoId.value) {
    const actual = visitas.find((v) => v.id === editandoId.value)
    const cambioFechaHora = actual.fecha !== form.value.fecha || actual.hora !== form.value.hora
    actualizarVisita(editandoId.value, {
      ...form.value,
      fincaNombre: finca.nombre,
      tecnicoNombre: tecnico.nombre,
      tecnicoCorreo: tecnico.correo,
    })
    // RF-06.5 — si hay cambio de fecha/hora, reenviar notificaciones
    if (cambioFechaHora) notificarCita(finca, tecnico, propietarioCorreo, form.value.fecha, form.value.hora, form.value.motivo, true)
  } else {
    crearVisita({
      ...form.value,
      cooperativaId: props.cooperativaId,
      fincaNombre: finca.nombre,
      tecnicoNombre: tecnico.nombre,
      tecnicoCorreo: tecnico.correo,
      propietarioCorreo,
    })
    // RF-06.2 — notificar al técnico y al propietario
    notificarCita(finca, tecnico, propietarioCorreo, form.value.fecha, form.value.hora, form.value.motivo)
    // RF-06.3 — recordatorios: día antes y mismo día (simulados programados)
    enviarCorreo(tecnico.correo, 'Recordatorio: visita mañana/mismo día — BioAgro', detalleCita(finca, tecnico, form.value.fecha, form.value.hora, form.value.motivo))
    enviarCorreo(propietarioCorreo, 'Recordatorio: visita mañana/mismo día — BioAgro', detalleCita(finca, tecnico, form.value.fecha, form.value.hora, form.value.motivo))
  }
  formularioVisible.value = false
}

// RF-06.4 — recordatorio manual de llamada al propietario, visible como tarea
const generarRecordatorio = (v) => actualizarVisita(v.id, { recordatorioManualPendiente: true })
const completarRecordatorio = (v) => actualizarVisita(v.id, { recordatorioManualPendiente: false })

// RF-06.6 — cancelar y notificar
const cancelar = (v) => {
  if (confirm(`¿Cancelar la visita a "${v.fincaNombre}"?`)) {
    cancelarVisita(v.id)
    enviarCorreo(v.tecnicoCorreo, 'Visita cancelada — BioAgro', `La visita del ${v.fecha} ${v.hora} a ${v.fincaNombre} fue cancelada.`)
    enviarCorreo(v.propietarioCorreo, 'Visita cancelada — BioAgro', `La visita del ${v.fecha} ${v.hora} a ${v.fincaNombre} fue cancelada.`)
  }
}

const registro = ref({ id: null, observaciones: '', resultado: '' })
const abrirRegistro = (v) => (registro.value = { id: v.id, observaciones: v.observaciones, resultado: v.resultado })
const guardarRegistro = () => {
  actualizarVisita(registro.value.id, {
    observaciones: registro.value.observaciones,
    resultado: registro.value.resultado,
    estado: 'Completada',
  })
  registro.value = { id: null, observaciones: '', resultado: '' }
}
</script>

<template>
  <section class="visitas">
    <div class="visitas__header">
      <h2>Visitas técnicas</h2>
      <button class="btn" @click="abrirCrear">+ Agendar visita</button>
    </div>

    <!-- Tareas pendientes RF-06.4 -->
    <div v-if="tareasPendientes.length" class="tareas">
      <h3>📞 Recordatorios de llamada pendientes</h3>
      <ul>
        <li v-for="v in tareasPendientes" :key="v.id">
          Llamar al propietario de {{ v.fincaNombre }} ({{ v.fecha }} {{ v.hora }})
          <button class="btn-mini" @click="completarRecordatorio(v)">Marcar hecho</button>
        </li>
      </ul>
    </div>

    <form v-if="formularioVisible" class="form" @submit.prevent="guardar">
      <h3>{{ editandoId ? 'Modificar visita' : 'Agendar visita' }}</h3>
      <label>
        Finca
        <select v-model="form.fincaId" required>
          <option value="" disabled>Seleccione</option>
          <option v-for="f in misFincas" :key="f.id" :value="f.id">{{ f.nombre }}</option>
        </select>
      </label>
      <label>
        Técnico
        <select v-model="form.tecnicoId" required>
          <option value="" disabled>Seleccione</option>
          <option v-for="t in misTecnicos" :key="t.id" :value="t.id">{{ t.nombre }} — {{ t.especialidad }}</option>
        </select>
      </label>
      <label>Fecha <input v-model="form.fecha" type="date" required /></label>
      <label>Hora <input v-model="form.hora" type="time" required /></label>
      <label>
        Motivo
        <select v-model="form.motivo" required>
          <option value="" disabled>Seleccione</option>
          <option>Seguimiento de alerta</option>
          <option>Revisión rutinaria</option>
          <option>Verificación de trampa</option>
        </select>
      </label>
      <div class="form__acciones">
        <button type="submit" class="btn">Guardar</button>
        <button type="button" class="btn-link" @click="formularioVisible = false">Cancelar</button>
      </div>
    </form>

    <table class="tabla">
      <thead>
        <tr><th>Finca</th><th>Técnico</th><th>Fecha</th><th>Hora</th><th>Motivo</th><th>Estado</th><th>Acciones</th></tr>
      </thead>
      <tbody>
        <tr v-for="v in misVisitas" :key="v.id">
          <td>{{ v.fincaNombre }}</td>
          <td>{{ v.tecnicoNombre }}</td>
          <td>{{ v.fecha }}</td>
          <td>{{ v.hora }}</td>
          <td>{{ v.motivo }}</td>
          <td><span class="badge" :class="'badge--' + v.estado.replace(' ', '')">{{ v.estado }}</span></td>
          <td class="acciones">
            <button class="btn-mini" @click="abrirEditar(v)">Modificar</button>
            <button class="btn-mini" @click="generarRecordatorio(v)">Recordatorio llamada</button>
            <button class="btn-mini" @click="abrirRegistro(v)">Registrar resultado</button>
            <button class="btn-mini btn-mini--danger" @click="cancelar(v)">Cancelar</button>
          </td>
        </tr>
        <tr v-if="misVisitas.length === 0">
          <td colspan="7" class="vacio">No hay visitas agendadas.</td>
        </tr>
      </tbody>
    </table>

    <!-- RF-06.8 — Registro de observaciones y resultado -->
    <form v-if="registro.id" class="form" @submit.prevent="guardarRegistro">
      <h3>Registrar resultado de visita</h3>
      <label>Observaciones <textarea v-model="registro.observaciones" rows="3"></textarea></label>
      <label>Resultado <textarea v-model="registro.resultado" rows="3"></textarea></label>
      <div class="form__acciones">
        <button type="submit" class="btn">Guardar y completar</button>
        <button type="button" class="btn-link" @click="registro.id = null">Cancelar</button>
      </div>
    </form>

    <div class="notif">
      <h3>📧 Últimas notificaciones enviadas</h3>
      <ul>
        <li v-for="(n, i) in notificaciones.slice(0, 5)" :key="i">
          <strong>{{ n.to }}</strong> — {{ n.asunto }} <small>({{ n.fecha }})</small>
        </li>
        <li v-if="notificaciones.length === 0" class="vacio">Sin notificaciones aún.</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.visitas { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.visitas__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.visitas__header h2 { font-family: 'DM Serif Display', serif; }
.tareas { background: #fff8e6; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.tareas h3 { margin-bottom: 8px; }
.tareas ul { list-style: none; display: flex; flex-direction: column; gap: 6px; }
.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; background: #f0e9db; }
.badge--Pendiente { background: var(--color-prioridad-seguimiento-bg); color: var(--color-prioridad-seguimiento); }
.badge--Encurso { background: #d1ecf1; color: #0c5460; }
.badge--Completada { background: var(--color-prioridad-ok-bg); color: var(--color-prioridad-ok); }
.badge--Cancelada { background: var(--color-prioridad-alta-bg); color: var(--color-prioridad-alta); }
.acciones { display: flex; gap: 6px; flex-wrap: wrap; }
.btn { background: #2D1B0E; color: #F7F5F0; border: none; border-radius: 999px; padding: 8px 18px; }
.btn:hover { background: #52B788; }
.btn-mini { border: 1px solid #ddd3c4; background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 12px; }
.btn-mini:hover { border-color: #52B788; }
.btn-mini--danger:hover { border-color: #c0392b; color: #c0392b; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; }
.vacio { text-align: center; color: #8a7a6a; padding: 12px; }
.form { display: flex; flex-direction: column; gap: 12px; max-width: 480px; margin-bottom: 16px; }
.form h3 { font-family: 'DM Serif Display', serif; }
.form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 4px; }
.form input, .form select, .form textarea { border: 1px solid #ddd3c4; border-radius: 10px; padding: 8px 12px; font-size: 14px; font-family: 'Inter', sans-serif; }
.form__acciones { display: flex; gap: 12px; align-items: center; }
.notif { margin-top: 20px; background: #F7F5F0; border-radius: 12px; padding: 16px; }
.notif ul { list-style: none; margin-top: 8px; display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
</style>
