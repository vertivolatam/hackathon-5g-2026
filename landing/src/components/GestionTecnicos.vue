<script setup>
import { ref, computed } from 'vue'
import { tecnicos, crearTecnico, actualizarTecnico, eliminarTecnico } from '../stores/tecnicos'
import { visitas } from '../stores/visitas'

const props = defineProps({ cooperativaId: { type: String, required: true } })

const misTecnicos = computed(() => tecnicos.filter((t) => t.cooperativaId === props.cooperativaId))

const visitasAsignadas = (tecnicoId) =>
  visitas.filter((v) => v.tecnicoId === tecnicoId && v.estado !== 'Completada' && v.estado !== 'Cancelada').length

const formularioVisible = ref(false)
const editandoId = ref(null)
const form = ref({ nombre: '', correo: '', telefono: '', especialidad: '' })

const abrirCrear = () => {
  editandoId.value = null
  form.value = { nombre: '', correo: '', telefono: '', especialidad: '' }
  formularioVisible.value = true
}

const abrirEditar = (t) => {
  editandoId.value = t.id
  form.value = { nombre: t.nombre, correo: t.correo, telefono: t.telefono, especialidad: t.especialidad }
  formularioVisible.value = true
}

const guardar = () => {
  if (editandoId.value) actualizarTecnico(editandoId.value, { ...form.value })
  else crearTecnico({ ...form.value, cooperativaId: props.cooperativaId })
  formularioVisible.value = false
}

const toggleActivo = (t) => actualizarTecnico(t.id, { activo: !t.activo })

const eliminar = (t) => {
  const pendientes = visitasAsignadas(t.id)
  if (pendientes > 0) {
    alert(`¡Atención! "${t.nombre}" tiene ${pendientes} visita(s) asignada(s) pendiente(s).`)
  }
  if (confirm(`¿Eliminar al técnico "${t.nombre}"?`)) eliminarTecnico(t.id)
}
</script>

<template>
  <section class="tecnicos">
    <div class="tecnicos__header">
      <h2>Gestión de técnicos</h2>
      <button class="btn" @click="abrirCrear">+ Nuevo técnico</button>
    </div>

    <form v-if="formularioVisible" class="form" @submit.prevent="guardar">
      <h3>{{ editandoId ? 'Editar técnico' : 'Registrar técnico' }}</h3>
      <label>Nombre <input v-model="form.nombre" required /></label>
      <label>Correo electrónico <input v-model="form.correo" type="email" required /></label>
      <label>Teléfono <input v-model="form.telefono" required /></label>
      <label>Especialidad <input v-model="form.especialidad" required /></label>
      <div class="form__acciones">
        <button type="submit" class="btn">Guardar</button>
        <button type="button" class="btn-link" @click="formularioVisible = false">Cancelar</button>
      </div>
    </form>

    <table v-else class="tabla">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Correo</th>
          <th>Teléfono</th>
          <th>Especialidad</th>
          <th>Disponibilidad</th>
          <th>Visitas asignadas</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in misTecnicos" :key="t.id">
          <td>{{ t.nombre }}</td>
          <td>{{ t.correo }}</td>
          <td>{{ t.telefono }}</td>
          <td>{{ t.especialidad }}</td>
          <td>
            <span class="badge" :class="t.disponible ? 'badge--ok' : 'badge--off'">
              {{ t.disponible ? 'Disponible' : 'Ocupado' }}
            </span>
          </td>
          <td>{{ visitasAsignadas(t.id) }}</td>
          <td>
            <span class="badge" :class="t.activo ? 'badge--ok' : 'badge--off'">
              {{ t.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </td>
          <td class="acciones">
            <button class="btn-mini" @click="abrirEditar(t)">Editar</button>
            <button class="btn-mini" @click="toggleActivo(t)">{{ t.activo ? 'Desactivar' : 'Activar' }}</button>
            <button class="btn-mini btn-mini--danger" @click="eliminar(t)">Eliminar</button>
          </td>
        </tr>
        <tr v-if="misTecnicos.length === 0">
          <td colspan="8" class="vacio">No hay técnicos registrados.</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.tecnicos { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.tecnicos__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.tecnicos__header h2 { font-family: 'DM Serif Display', serif; }
.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; }
.badge--ok { background: var(--color-prioridad-ok-bg); color: var(--color-prioridad-ok); }
.badge--off { background: var(--color-prioridad-alta-bg); color: var(--color-prioridad-alta); }
.acciones { display: flex; gap: 6px; flex-wrap: wrap; }
.btn { background: #2D1B0E; color: #F7F5F0; border: none; border-radius: 999px; padding: 8px 18px; }
.btn:hover { background: #52B788; }
.btn-mini { border: 1px solid #ddd3c4; background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 12px; }
.btn-mini:hover { border-color: #52B788; }
.btn-mini--danger:hover { border-color: #c0392b; color: #c0392b; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; }
.vacio { text-align: center; color: #8a7a6a; padding: 24px; }
.form { display: flex; flex-direction: column; gap: 12px; max-width: 480px; }
.form h3 { font-family: 'DM Serif Display', serif; }
.form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 4px; }
.form input { border: 1px solid #ddd3c4; border-radius: 10px; padding: 8px 12px; font-size: 14px; }
.form__acciones { display: flex; gap: 12px; align-items: center; }
</style>
