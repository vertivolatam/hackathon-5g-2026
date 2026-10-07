// RNF-06.2 / RNF-05.3 — Servicio de correo desacoplado con reintentos (RNF-04.3).
import { notificaciones } from '../stores/notificaciones'

const MAX_REINTENTOS = 3

// Simula el envío: en producción sería fetch() al proveedor SMTP/API.
const intentarEnvio = async (to, asunto) => {
  // ~30% de fallos simulados para demostrar el reintento
  if (Math.random() < 0.3) throw new Error('Fallo transitorio del servicio de correo')
  return true
}

export const enviarCorreo = async (to, asunto, cuerpo) => {
  let ultimoError = null
  for (let intento = 1; intento <= MAX_REINTENTOS; intento++) {
    try {
      await intentarEnvio(to, asunto)
      notificaciones.unshift({ to, asunto, cuerpo, fecha: new Date().toLocaleString(), estado: 'Enviado' })
      console.log(`📧 Correo enviado a ${to}: ${asunto} (intento ${intento})`)
      return true
    } catch (error) {
      ultimoError = error
      console.warn(`⚠️ Fallo enviando a ${to}, reintentando (${intento}/${MAX_REINTENTOS})...`)
      await new Promise((r) => setTimeout(r, 300 * intento))
    }
  }
  notificaciones.unshift({ to, asunto, cuerpo, fecha: new Date().toLocaleString(), estado: 'Fallido' })
  console.error(`❌ No se pudo enviar a ${to}: ${ultimoError.message}`)
  return false
}
