import { reactive, watch } from 'vue'

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

export const crearCooperativa = (datos) => {
  cooperativas.push({ id: crypto.randomUUID(), activa: true, ...datos })
}

export const actualizarCooperativa = (id, datos) => {
  const idx = cooperativas.findIndex((c) => c.id === id)
  if (idx !== -1) cooperativas[idx] = { ...cooperativas[idx], ...datos }
}

export const toggleEstadoCooperativa = (id) => {
  const coop = cooperativas.find((c) => c.id === id)
  if (coop) coop.activa = !coop.activa
}

export const eliminarCooperativa = (id) => {
  const idx = cooperativas.findIndex((c) => c.id === id)
  if (idx !== -1) cooperativas.splice(idx, 1)
}
