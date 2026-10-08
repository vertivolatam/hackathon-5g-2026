import { reactive, watch } from 'vue'
import { api } from '../services/api'

const guardadas = localStorage.getItem('bioagro_cooperativas')

export const cooperativas = reactive(
  guardadas
    ? JSON.parse(guardadas)
    : [
        {
          id: 'coop-1',
          nombre: 'Cooperativa San José',
          region: 'Valle Central',
          correo: 'contacto@coopsj.cr',
          logo: '',
          activa: true,
        },
      ],
)

watch(
  cooperativas,
  (val) => localStorage.setItem('bioagro_cooperativas', JSON.stringify(val)),
  { deep: true, immediate: true },
)

// Sincronización con la API real (fallback: datos locales si la API no responde)
api.listar('cooperativas')
  .then((res) => {
    if (Array.isArray(res.items)) {
      cooperativas.splice(0, cooperativas.length, ...res.items)
    }
  })
  .catch(() => {})

export const crearCooperativa = (datos) => {
  const nueva = { id: crypto.randomUUID(), activa: true, ...datos }
  cooperativas.push(nueva)
  api.crear('cooperativas', nueva).catch(() => {})
}

export const actualizarCooperativa = (id, datos) => {
  const idx = cooperativas.findIndex((c) => c.id === id)
  if (idx !== -1) {
    cooperativas[idx] = { ...cooperativas[idx], ...datos }
    api.actualizar('cooperativas', id, datos).catch(() => {})
  }
}

export const toggleEstadoCooperativa = (id) => {
  const coop = cooperativas.find((c) => c.id === id)
  if (coop) {
    coop.activa = !coop.activa
    api.actualizar('cooperativas', id, { activa: coop.activa }).catch(() => {})
  }
}

export const eliminarCooperativa = (id) => {
  const idx = cooperativas.findIndex((c) => c.id === id)
  if (idx !== -1) {
    cooperativas.splice(idx, 1)
    api.eliminar('cooperativas', id).catch(() => {})
  }
}
