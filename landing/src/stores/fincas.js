import { reactive, watch } from 'vue'

const guardadas = localStorage.getItem('bioagro_fincas')

export const fincas = reactive(
  guardadas
    ? JSON.parse(guardadas)
    : [
        {
          id: 'finca-1',
          cooperativaId: 'coop-1',
          nombre: 'Finca El Cafetal',
          propietario: 'Juan Pérez',
          area: 12.5,
          descripcion: 'Cafetal en ladera con sistema de riego por goteo.',
          poligono: [
            [9.9281, -84.0907],
            [9.931, -84.088],
            [9.9335, -84.0915],
            [9.9305, -84.094],
          ],
          sensores: [
            { id: 's1', nombre: 'Sensor humedad A', lat: 9.9305, lng: -84.0905, activo: true },
            { id: 's2', nombre: 'Sensor plaga B', lat: 9.9318, lng: -84.0912, activo: false },
          ],
          riesgo: 'Medio',
          ultimaAlerta: '2026-10-05 — Captura de broca 12% sobre umbral',
          visitasPendientes: 1,
          prioridad: 'Alta',
          lecturaActual: {
            fecha: '2026-10-06 08:30',
            temperatura: 24.5,
            humedad: 78,
            plagas: [{ tipo: 'Broca', severidad: 62 }],
          },
          detecciones: [
            { fecha: '2026-10-05', tipo: 'Broca', severidad: 62 },
            { fecha: '2026-10-03', tipo: 'Roya', severidad: 28 },
            { fecha: '2026-09-28', tipo: 'Broca', severidad: 45 },
            { fecha: '2026-09-20', tipo: 'Ojo de gallo', severidad: 15 },
          ],
          tendenciaSeveridad: [
            { periodo: 'May', severidad: 20 },
            { periodo: 'Jun', severidad: 35 },
            { periodo: 'Jul', severidad: 42 },
            { periodo: 'Ago', severidad: 38 },
            { periodo: 'Sep', severidad: 55 },
            { periodo: 'Oct', severidad: 62 },
          ],
          actividadSensores: [
            { periodo: 'May', activos: 2 },
            { periodo: 'Jun', activos: 2 },
            { periodo: 'Jul', activos: 3 },
            { periodo: 'Ago', activos: 3 },
            { periodo: 'Sep', activos: 4 },
            { periodo: 'Oct', activos: 4 },
          ],
        },
      ],
)

watch(
  fincas,
  (val) => localStorage.setItem('bioagro_fincas', JSON.stringify(val)),
  { deep: true, immediate: true },
)

export const crearFinca = (datos) => {
  fincas.push({
    id: crypto.randomUUID(),
    sensores: [],
    riesgo: 'Bajo',
    ultimaAlerta: '—',
    visitasPendientes: 0,
    prioridad: 'Sin prioridad inmediata',
    lecturaActual: null,
    detecciones: [],
    tendenciaSeveridad: [],
    actividadSensores: [],
    ...datos,
  })
}

export const actualizarFinca = (id, datos) => {
  const idx = fincas.findIndex((f) => f.id === id)
  if (idx !== -1) fincas[idx] = { ...fincas[idx], ...datos }
}

export const eliminarFinca = (id) => {
  const idx = fincas.findIndex((f) => f.id === id)
  if (idx !== -1) fincas.splice(idx, 1)
}
