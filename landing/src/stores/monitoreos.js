import { reactive, watch } from 'vue'

const guardados = localStorage.getItem('bioagro_monitoreos')

export const monitoreos = reactive(guardados ? JSON.parse(guardados) : [])

watch(
  monitoreos,
  (val) => localStorage.setItem('bioagro_monitoreos', JSON.stringify(val)),
  { deep: true, immediate: true },
)

export const crearMonitoreo = (datos) => {
  monitoreos.unshift({ id: crypto.randomUUID(), ...datos })
}
