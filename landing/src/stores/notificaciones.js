import { reactive } from 'vue'

// Registro en memoria de correos "enviados" (mock: sin backend real).
// El envío con reintentos vive en src/services/correoService.js (RNF-04.3).
export const notificaciones = reactive([])
