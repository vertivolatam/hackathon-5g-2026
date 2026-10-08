import { reactive, watch } from 'vue'
import { api } from '../services/api'

const guardadas = localStorage.getItem('bioagro_visitas')

export const visitas = reactive(
  guardadas
    ? JSON.parse(guardadas)
    : [
        {
          id: 'visita-1',
          cooperativaId: 'coop-1',
          fincaId: 'finca-1',
          tecnicoId: 'tec-1',
          fincaNombre: 'Finca El Cafetal',
          tecnicoNombre: 'María López',
          tecnicoCorreo: 'tecnico@bioagro.cr',
          propietarioCorreo: 'juan.perez@example.com',
          fecha: '2026-10-10',
          hora: '09:00',
          motivo: 'Seguimiento de alerta',
          estado: 'Pendiente',
          observaciones: '',
          resultado: '',
          recordatorioManualPendiente: false,
        },
      ],
)

watch(
  visitas,
  (val) => localStorage.setItem('bioagro_visitas', JSON.stringify(val)),
  { deep: true, immediate: true },
)

api.listar('visitas')
  .then((res) => {
    if (Array.isArray(res.items)) visitas.splice(0, visitas.length, ...res.items)
  })
  .catch(() => {})

export const crearVisita = (datos) => {
  const nueva = { id: crypto.randomUUID(), estado: 'Pendiente', observaciones: '', resultado: '', recordatorioManualPendiente: false, ...datos }
  visitas.push(nueva)
  api.crear('visitas', nueva).catch(() => {})
}

export const actualizarVisita = (id, datos) => {
  const idx = visitas.findIndex((v) => v.id === id)
  if (idx !== -1) {
    visitas[idx] = { ...visitas[idx], ...datos }
    api.actualizar('visitas', id, datos).catch(() => {})
  }
}

export const cancelarVisita = (id) => {
  const visita = visitas.find((v) => v.id === id)
  if (visita) {
    visita.estado = 'Cancelada'
    api.actualizar('visitas', id, { estado: 'Cancelada' }).catch(() => {})
  }
}
