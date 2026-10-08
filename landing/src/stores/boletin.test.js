import { describe, it, expect } from 'vitest'
import { distanciaKm } from './boletin'

describe('distanciaKm', () => {
  it('devuelve ~0 para el mismo punto', () => {
    expect(distanciaKm(9.9281, -84.0907, 9.9281, -84.0907)).toBeLessThan(0.01)
  })

  it('calcula distancia aproximada entre dos puntos conocidos', () => {
    // San José → ~1 grado de latitud ≈ 111 km
    const d = distanciaKm(9.9281, -84.0907, 10.9281, -84.0907)
    expect(d).toBeGreaterThan(100)
    expect(d).toBeLessThan(120)
  })
})
