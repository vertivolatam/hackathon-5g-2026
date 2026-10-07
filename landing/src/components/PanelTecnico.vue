<script setup>
import { ref, computed } from 'vue'
import { visitas, actualizarVisita } from '../stores/visitas'

const props = defineProps({ email: { type: String, required: true } })

const misVisitas = computed(() => visitas.filter((v) => v.tecnicoCorreo === props.email))

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

const marcarEnCurso = (v) => actualizarVisita(v.id, { estado: 'En curso' })
</script>

<template>
  <section class="panel">
    <h2>Mis visitas asignadas</h2>

    <table class="tabla">
      <thead>
        <tr><th>Finca</th><th>Fecha</th><th>Hora</th><th>Motivo</th><th>Estado</th><th>Acciones</th></tr>
      </thead>
      <tbody>
        <tr v-for="v in misVisitas" :key="v.id">
          <td>{{ v.fincaNombre }}</td>
          <td>{{ v.fecha }}</td>
          <td>{{ v.hora }}</td>
          <td>{{ v.motivo }}</td>
          <td><span class="badge" :class="'badge--' + v.estado.replace(' ', '')">{{ v.estado }}</span></td>
          <td class="acciones">
            <button v-if="v.estado === 'Pendiente'" class="btn-mini" @click="marcarEnCurso(v)">Iniciar</button>
            <button v-if="v.estado !== 'Cancelada' && v.estado !== 'Completada'" class="btn-mini" @click="abrirRegistro(v)">Completar</button>
          </td>
        </tr>
        <tr v-if="misVisitas.length === 0">
          <td colspan="6" class="vacio">No tienes visitas asignadas.</td>
        </tr>
      </tbody>
    </table>

    <form v-if="registro.id" class="form" @submit.prevent="guardarRegistro">
      <h3>Registrar observaciones y resultado</h3>
      <label>Observaciones <textarea v-model="registro.observaciones" rows="3"></textarea></label>
      <label>Resultado <textarea v-model="registro.resultado" rows="3"></textarea></label>
      <div class="form__acciones">
        <button type="submit" class="btn">Guardar visita</button>
        <button type="button" class="btn-link" @click="registro.id = null">Cancelar</button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.panel { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.panel h2 { font-family: 'DM Serif Display', serif; margin-bottom: 16px; }
.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; background: #f0e9db; }
.badge--Pendiente { background: var(--color-prioridad-seguimiento-bg); color: var(--color-prioridad-seguimiento); }
.badge--Encurso { background: #d1ecf1; color: #0c5460; }
.badge--Completada { background: var(--color-prioridad-ok-bg); color: var(--color-prioridad-ok); }
.badge--Cancelada { background: var(--color-prioridad-alta-bg); color: var(--color-prioridad-alta); }
.acciones { display: flex; gap: 6px; }
.btn { background: #2D1B0E; color: #F7F5F0; border: none; border-radius: 999px; padding: 8px 18px; }
.btn:hover { background: #52B788; }
.btn-mini { border: 1px solid #ddd3c4; background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 12px; }
.btn-mini:hover { border-color: #52B788; }
.btn-link { background: none; border: none; color: #52B788; font-size: 13px; }
.vacio { text-align: center; color: #8a7a6a; padding: 12px; }
.form { display: flex; flex-direction: column; gap: 12px; max-width: 480px; margin-top: 16px; }
.form h3 { font-family: 'DM Serif Display', serif; }
.form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 4px; }
.form textarea { border: 1px solid #ddd3c4; border-radius: 10px; padding: 8px 12px; font-size: 14px; font-family: 'Inter', sans-serif; }
.form__acciones { display: flex; gap: 12px; align-items: center; }
</style>
