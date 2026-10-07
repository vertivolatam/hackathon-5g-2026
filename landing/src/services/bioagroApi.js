// RNF-04.2 / RNF-05.3 — Origen de datos BioAgro desacoplado: mock intercambiable por API real.
import { fincas } from '../stores/fincas'

const API_URL = import.meta.env.VITE_API_BIOAGRO_URL

// Caché local: último dato disponible por finca, con timestamp
const cache = {}

export const obtenerLecturaFinca = async (fincaId) => {
  try {
    // En producción: fetch(`${API_URL}/fincas/${fincaId}/ultima-lectura`)
    const finca = fincas.find((f) => f.id === fincaId)
    if (!finca || !finca.lecturaActual) throw new Error('Sin datos')
    cache[fincaId] = { lectura: finca.lecturaActual, obtenidoEn: new Date().toISOString() }
    return { ...cache[fincaId], origen: 'api' }
  } catch (error) {
    // Error de conexión: devolver último dato disponible con indicación de fecha/hora
    if (cache[fincaId]) {
      return { ...cache[fincaId], origen: 'cache', error: error.message }
    }
    throw error
  }
}
