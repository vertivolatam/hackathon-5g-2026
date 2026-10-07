<script setup>
import { ref } from 'vue'
import {
  cooperativas,
  crearCooperativa,
  actualizarCooperativa,
  toggleEstadoCooperativa,
  eliminarCooperativa,
} from '../stores/cooperativas'

const formularioVisible = ref(false)
const editandoId = ref(null)
const dashboardCoop = ref(null)

const form = ref({ nombre: '', region: '', correo: '', logo: '' })

const abrirCrear = () => {
  editandoId.value = null
  form.value = { nombre: '', region: '', correo: '', logo: '' }
  formularioVisible.value = true
}

const abrirEditar = (coop) => {
  editandoId.value = coop.id
  form.value = { nombre: coop.nombre, region: coop.region, correo: coop.correo, logo: coop.logo }
  formularioVisible.value = true
}

const guardar = () => {
  if (editandoId.value) {
    actualizarCooperativa(editandoId.value, { ...form.value })
  } else {
    crearCooperativa({ ...form.value })
  }
  formularioVisible.value = false
}

const eliminar = (coop) => {
  if (confirm(`¿Eliminar la cooperativa "${coop.nombre}"?`)) {
    eliminarCooperativa(coop.id)
  }
}
</script>

<template>
  <section class="gestion">
    <div class="gestion__header">
      <h2>Gestión de cooperativas</h2>
      <button class="btn" @click="abrirCrear">+ Nueva cooperativa</button>
    </div>

    <!-- Dashboard en modo lectura (RF-01.5) -->
    <div v-if="dashboardCoop" class="dashboard">
      <button class="btn-link" @click="dashboardCoop = null">← Volver al listado</button>
      <h3>Dashboard de {{ dashboardCoop.nombre }} <small>(solo lectura)</small></h3>
      <div class="dashboard__grid">
        <div class="dato"><span class="dato__num">—</span><span class="dato__label">Fincas registradas</span></div>
        <div class="dato"><span class="dato__num">—</span><span class="dato__label">Técnicos activos</span></div>
        <div class="dato"><span class="dato__num">—</span><span class="dato__label">Visitas este mes</span></div>
      </div>
      <p><strong>Región:</strong> {{ dashboardCoop.region }} · <strong>Contacto:</strong> {{ dashboardCoop.correo }} · <strong>Estado:</strong> {{ dashboardCoop.activa ? 'Activa' : 'Inactiva' }}</p>
    </div>

    <!-- Formulario crear/editar (RF-01.1, RF-01.2) -->
    <form v-if="formularioVisible" class="form" @submit.prevent="guardar">
      <h3>{{ editandoId ? 'Editar cooperativa' : 'Registrar cooperativa' }}</h3>
      <label>Nombre <input v-model="form.nombre" required /></label>
      <label>Región <input v-model="form.region" required /></label>
      <label>Correo de contacto <input v-model="form.correo" type="email" required /></label>
      <label>Logo (URL) <input v-model="form.logo" placeholder="https://..." /></label>
      <div class="form__acciones">
        <button type="submit" class="btn">Guardar</button>
        <button type="button" class="btn-link" @click="formularioVisible = false">Cancelar</button>
      </div>
    </form>

    <!-- Listado (RF-01.4) -->
    <table v-else class="tabla">
      <thead>
        <tr>
          <th>Logo</th>
          <th>Nombre</th>
          <th>Región</th>
          <th>Correo</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="coop in cooperativas" :key="coop.id">
          <td><img v-if="coop.logo" :src="coop.logo" class="logo" alt="logo" /><span v-else>—</span></td>
          <td>{{ coop.nombre }}</td>
          <td>{{ coop.region }}</td>
          <td>{{ coop.correo }}</td>
          <td>
            <span class="badge" :class="coop.activa ? 'badge--ok' : 'badge--off'">
              {{ coop.activa ? 'Activa' : 'Inactiva' }}
            </span>
          </td>
          <td class="acciones">
            <button class="btn-mini" @click="abrirEditar(coop)">Editar</button>
            <button class="btn-mini" @click="dashboardCoop = coop">Dashboard</button>
            <button class="btn-mini" @click="toggleEstadoCooperativa(coop.id)">
              {{ coop.activa ? 'Desactivar' : 'Activar' }}
            </button>
            <button class="btn-mini btn-mini--danger" @click="eliminar(coop)">Eliminar</button>
          </td>
        </tr>
        <tr v-if="cooperativas.length === 0">
          <td colspan="6" class="vacio">No hay cooperativas registradas.</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.gestion { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.gestion__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.gestion__header h2 { font-family: 'DM Serif Display', serif; }

.btn { background: #2D1B0E; color: #F7F5F0; border: none; border-radius: 999px; padding: 8px 18px; }
.btn:hover { background: #52B788; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; }

.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-weight: 600; font-size: 12px; text-transform: uppercase; }
.logo { width: 32px; height: 32px; border-radius: 8px; object-fit: cover; }

.badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; }
.badge--ok { background: var(--color-prioridad-ok-bg); color: var(--color-prioridad-ok); }
.badge--off { background: var(--color-prioridad-alta-bg); color: var(--color-prioridad-alta); }

.acciones { display: flex; gap: 6px; flex-wrap: wrap; }
.btn-mini { border: 1px solid #ddd3c4; background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 12px; }
.btn-mini:hover { border-color: #52B788; color: #2d7a4f; }
.btn-mini--danger:hover { border-color: #c0392b; color: #c0392b; }
.vacio { text-align: center; color: #8a7a6a; padding: 24px; }

.form { display: flex; flex-direction: column; gap: 12px; max-width: 480px; }
.form h3 { font-family: 'DM Serif Display', serif; }
.form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 4px; }
.form input { border: 1px solid #ddd3c4; border-radius: 10px; padding: 8px 12px; font-size: 14px; }
.form__acciones { display: flex; gap: 12px; align-items: center; }

.dashboard { display: flex; flex-direction: column; gap: 12px; }
.dashboard h3 { font-family: 'DM Serif Display', serif; }
.dashboard h3 small { font-family: 'Inter', sans-serif; color: #8a7a6a; font-size: 12px; }
.dashboard__grid { display: flex; gap: 16px; }
.dato { background: #F7F5F0; border-radius: 12px; padding: 16px 24px; display: flex; flex-direction: column; align-items: center; }
.dato__num { font-size: 24px; font-weight: 600; color: #52B788; }
.dato__label { font-size: 12px; color: #8a7a6a; }
</style>
