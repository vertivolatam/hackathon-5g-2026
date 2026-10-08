import { reactive, watch } from 'vue'
import { api } from '../services/api'

const guardados = localStorage.getItem('bioagro_tecnicos')

export const tecnicos = reactive(
  guardados
    ? JSON.parse(guardados)
    : [
        {
          id: 'tec-1',
          cooperativaId: 'coop-1',
          nombre: 'María López',
          correo: 'tecnico@bioagro.cr',
          telefono: '8888-0000',
          especialidad: 'Fitosanidad',
          disponible: true,
          activo: true,
        },
      ],
)

watch(
  tecnicos,
  (val) => localStorage.setItem('bioagro_tecnicos', JSON.stringify(val)),
  { deep: true, immediate: true },
)

api.listar('tecnicos')
  .then((res) => {
    if (Array.isArray(res.items)) tecnicos.splice(0, tecnicos.length, ...res.items)
  })
  .catch(() => {})

export const crearTecnico = (datos) => {
  const nuevo = { id: crypto.randomUUID(), disponible: true, activo: true, ...datos }
  tecnicos.push(nuevo)
  api.crear('tecnicos', nuevo).catch(() => {})
}

export const actualizarTecnico = (id, datos) => {
  const idx = tecnicos.findIndex((t) => t.id === id)
  if (idx !== -1) {
    tecnicos[idx] = { ...tecnicos[idx], ...datos }
    api.actualizar('tecnicos', id, datos).catch(() => {})
  }
}

export const eliminarTecnico = (id) => {
  const idx = tecnicos.findIndex((t) => t.id === id)
  if (idx !== -1) {
    tecnicos.splice(idx, 1)
    api.eliminar('tecnicos', id).catch(() => {})
  }
}
