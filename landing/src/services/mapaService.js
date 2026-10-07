// RNF-06.2 / RNF-05.3 — Integración de mapas abstraída en un módulo independiente.
// Cambiar de proveedor (OSM → Mapbox → Google) solo requiere modificar este archivo.
export const TILE_LAYER_URL = import.meta.env.VITE_MAP_TILES_URL
export const TILE_LAYER_ATTRIBUTION = import.meta.env.VITE_MAP_ATTRIBUTION
