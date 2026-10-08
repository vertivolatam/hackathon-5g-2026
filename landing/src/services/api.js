// Capa de acceso a la API real (FastAPI). Sustituye progresivamente
// los stores basados en localStorage.
const API = import.meta.env.VITE_API_BIOAGRO_URL

const obtenerToken = () => {
  try {
    const sesion = JSON.parse(localStorage.getItem('bioagro_sesion') || 'null')
    return sesion?.token || ''
  } catch {
    return ''
  }
}

const req = async (path, options = {}) => {
  const token = obtenerToken()
  if (!token) throw new Error('No autenticado')
  const resp = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    ...options,
  })
  if (resp.status === 401) {
    // Sesión expirada o inválida: forzar nuevo login
    localStorage.removeItem('bioagro_sesion')
    location.reload()
    throw new Error('Sesión expirada')
  }
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  if (resp.status === 204) return null
  return resp.json()
}

export const api = {
  listar: (recurso, cooperativaId) =>
    req(`/api/${recurso}${cooperativaId ? `?cooperativaId=${cooperativaId}` : ''}`),
  crear: (recurso, datos) => req(`/api/${recurso}`, { method: 'POST', body: JSON.stringify(datos) }),
  actualizar: (recurso, id, datos) => req(`/api/${recurso}/${id}`, { method: 'PUT', body: JSON.stringify(datos) }),
  eliminar: (recurso, id) => req(`/api/${recurso}/${id}`, { method: 'DELETE' }),
}
