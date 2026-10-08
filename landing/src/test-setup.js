// Mocks mínimos para correr stores en Node (sin navegador)
const store = {}
globalThis.localStorage = {
  getItem: (k) => store[k] ?? null,
  setItem: (k, v) => { store[k] = String(v) },
  removeItem: (k) => { delete store[k] },
  clear: () => { for (const k of Object.keys(store)) delete store[k] },
}
globalThis.fetch = async () => ({ ok: false, status: 500, json: async () => ({}) })
