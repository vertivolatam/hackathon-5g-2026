import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from './api'

describe('api service', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('envía el token Bearer cuando hay sesión', async () => {
    localStorage.setItem('bioagro_sesion', JSON.stringify({ token: 'tok123' }))
    const spy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ count: 0, items: [] }),
    })
    await api.listar('fincas')
    const [, options] = spy.mock.calls[0]
    expect(options.headers.Authorization).toBe('Bearer tok123')
  })

  it('lanza error si no hay sesión', async () => {
    await expect(api.listar('fincas')).rejects.toThrow('No autenticado')
  })

  it('construye la URL con cooperativaId', async () => {
    localStorage.setItem('bioagro_sesion', JSON.stringify({ token: 't' }))
    const spy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ count: 0, items: [] }),
    })
    await api.listar('fincas', 'coop-1')
    const [url] = spy.mock.calls[0]
    expect(url).toContain('/api/fincas?cooperativaId=coop-1')
  })
})
