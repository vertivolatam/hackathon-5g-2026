import { reactive, watch } from 'vue'

const guardadas = localStorage.getItem('bioagro_evidencias')

export const evidencias = reactive(guardadas ? JSON.parse(guardadas) : [])

watch(
  evidencias,
  (val) => localStorage.setItem('bioagro_evidencias', JSON.stringify(val)),
  { deep: true, immediate: true },
)

export const crearEvidencia = (datos) => {
  evidencias.unshift({ id: crypto.randomUUID(), ...datos })
}
