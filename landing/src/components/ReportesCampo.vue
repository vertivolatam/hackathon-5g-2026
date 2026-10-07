<script setup>
import { computed } from 'vue'
import { monitoreos } from '../stores/monitoreos'
import { evidencias } from '../stores/evidencias'
import { tecnicos } from '../stores/tecnicos'

const props = defineProps({ cooperativaId: { type: String, required: true } })

// Técnicos de esta cooperativa → sus reportes de campo
const correosTecnicos = computed(() =>
  new Set(tecnicos.filter((t) => t.cooperativaId === props.cooperativaId).map((t) => t.correo)),
)

const misMonitoreos = computed(() => monitoreos.filter((m) => correosTecnicos.value.has(m.tecnicoEmail)))
const misEvidencias = computed(() => evidencias.filter((e) => correosTecnicos.value.has(e.tecnicoEmail)))
</script>

<template>
  <section class="reportes">
    <h2>Reportes de campo de los técnicos</h2>

    <h3>Evidencias de plagas</h3>
    <ul class="evidencias">
      <li v-for="e in misEvidencias" :key="e.id">
        <img v-if="e.imagen" :src="e.imagen" alt="evidencia" />
        <div>
          <strong>{{ e.plaga }}</strong> — {{ e.severidad }}% · {{ e.fecha }} · {{ e.finca }}
          <p class="meta">Técnico: {{ e.tecnicoEmail }}</p>
          <p>{{ e.descripcion }}</p>
        </div>
      </li>
      <li v-if="misEvidencias.length === 0" class="vacio">Sin evidencias registradas por los técnicos.</li>
    </ul>

    <h3>Resultados de monitoreos</h3>
    <table class="tabla">
      <thead>
        <tr><th>Fecha</th><th>Finca</th><th>Tipo</th><th>Observaciones</th><th>Técnico</th></tr>
      </thead>
      <tbody>
        <tr v-for="m in misMonitoreos" :key="m.id">
          <td>{{ m.fecha }}</td>
          <td>{{ m.finca }}</td>
          <td>{{ m.tipo }}</td>
          <td>{{ m.observaciones }}</td>
          <td>{{ m.tecnicoEmail }}</td>
        </tr>
        <tr v-if="misMonitoreos.length === 0">
          <td colspan="5" class="vacio">Sin monitoreos registrados.</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.reportes { font-family: 'Inter', sans-serif; padding: 24px; background: #fff; border-bottom: 1px solid #ece5d8; }
.reportes h2 { font-family: 'DM Serif Display', serif; margin-bottom: 16px; }
.reportes h3 { font-family: 'DM Serif Display', serif; margin: 16px 0 8px; }
.evidencias { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.evidencias li { display: flex; gap: 12px; background: #F7F5F0; border-radius: 12px; padding: 12px; font-size: 14px; }
.evidencias img { width: 80px; height: 80px; object-fit: cover; border-radius: 10px; }
.evidencias p { color: #8a7a6a; font-size: 13px; margin-top: 4px; }
.meta { font-style: italic; }
.tabla { width: 100%; border-collapse: collapse; }
.tabla th, .tabla td { text-align: left; padding: 10px; border-bottom: 1px solid #f0e9db; font-size: 14px; }
.tabla th { color: #8a7a6a; font-size: 12px; text-transform: uppercase; }
.vacio { color: #8a7a6a; text-align: center; padding: 12px; }
</style>
