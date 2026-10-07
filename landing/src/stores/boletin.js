import { reactive, watch } from 'vue'

const guardadas = localStorage.getItem('bioagro_incidencias')

export const incidencias = reactive(
  guardadas
    ? JSON.parse(guardadas)
    : [
        { id: 'i1', tipo: 'Broca del café', severidad: 85, nivelRiesgo: 'Alta', lat: 9.9295, lng: -84.0912, fecha: '2026-10-06', finca: 'Finca La Palmera (ajena)' },
        { id: 'i2', tipo: 'Roya del café', severidad: 30, nivelRiesgo: 'Media', lat: 9.94, lng: -84.1, fecha: '2026-10-05', finca: 'Finca El Mirador (ajena)' },
        { id: 'i3', tipo: 'Ojo de gallo', severidad: 12, nivelRiesgo: 'Baja', lat: 9.96, lng: -84.08, fecha: '2026-10-03', finca: 'Beneficios del Sur' },
        { id: 'i4', tipo: 'Broca del café', severidad: 55, nivelRiesgo: 'Alta', lat: 9.935, lng: -84.085, fecha: '2026-10-01', finca: 'Finca La Cresta (ajena)' },
      ],
)

watch(
  incidencias,
  (val) => localStorage.setItem('bioagro_incidencias', JSON.stringify(val)),
  { deep: true, immediate: true },
)

export const registrarIncidencia = (datos) => {
  incidencias.unshift({ id: crypto.randomUUID(), ...datos })
}

// Distancia en km entre dos puntos (Haversine)
export const distanciaKm = (lat1, lng1, lat2, lng2) => {
  const R = 6371
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLng = ((lng2 - lng1) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}
