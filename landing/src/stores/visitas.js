import { reactive, watch } from 'vue'

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

export const crearVisita = (datos) => {
  visitas.push({ id: crypto.randomUUID(), estado: 'Pendiente', observaciones: '', resultado: '', recordatorioManualPendiente: false, ...datos })
}

export const actualizarVisita = (id, datos) => {
  const idx = visitas.findIndex((v) => v.id === id)
  if (idx !== -1) visitas[idx] = { ...visitas[idx], ...datos }
}

export const cancelarVisita = (id) => {
  const visita = visitas.find((v) => v.id === id)
  if (visita) visita.estado = 'Cancelada'
}
