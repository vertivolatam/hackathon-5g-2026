import { reactive, watch } from 'vue'

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

export const crearTecnico = (datos) => {
  tecnicos.push({ id: crypto.randomUUID(), disponible: true, activo: true, ...datos })
}

export const actualizarTecnico = (id, datos) => {
  const idx = tecnicos.findIndex((t) => t.id === id)
  if (idx !== -1) tecnicos[idx] = { ...tecnicos[idx], ...datos }
}

export const eliminarTecnico = (id) => {
  const idx = tecnicos.findIndex((t) => t.id === id)
  if (idx !== -1) tecnicos.splice(idx, 1)
}
