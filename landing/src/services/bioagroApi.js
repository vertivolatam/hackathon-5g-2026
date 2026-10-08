// RNF-04.2 / RNF-05.3 — Origen de datos BioAgro desacoplado.
// Hoy consulta el backend FastAPI real (/api/telemetry/latest); si la API
// falla, devuelve el último dato en caché con su fecha/hora de actualización.
import { fincas } from '../stores/fincas'

const API_URL = import.meta.env.VITE_API_BIOAGRO_URL

const cache = {}

const mockLectura = (fincaId) => {
  const finca = fincas.find((f) => f.id === fincaId)
  return finca?.lecturaActual || null
}

export const obtenerLecturaFinca = async (fincaId) => {
  try {
    const resp = await fetch(`${API_URL}/api/telemetry/latest`, { signal: AbortSignal.timeout(5000) })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    const lectura = {
      fecha: data.ts,
      temperatura: data.payload?.temperatura ?? null,
      humedad: data.payload?.humedad ?? null,
      plagas: data.payload?.plagas ?? [],
    }
    cache[fincaId] = { lectura, obtenidoEn: new Date().toISOString() }
    return { ...cache[fincaId], origen: 'api' }
  } catch (error) {
    // Error de conexión: último dato disponible con indicación de fecha/hora
    if (cache[fincaId]) {
      return { ...cache[fincaId], origen: 'cache', error: error.message }
    }
    const mock = mockLectura(fincaId)
    if (mock) {
      cache[fincaId] = { lectura: mock, obtenidoEn: new Date().toISOString() }
      return { lectura: mock, obtenidoEn: cache[fincaId].obtenidoEn, origen: 'cache', error: error.message }
    }
    throw error
  }
}

export const obtenerDetecciones = async (limit = 20) => {
  const resp = await fetch(`${API_URL}/api/detections?limit=${limit}`)
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  return resp.json()
}
