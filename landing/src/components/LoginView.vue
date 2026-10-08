<script setup>
import { ref } from 'vue'

const emit = defineEmits(['login', 'volver'])

const email = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

// RF-02.3 — Recuperación de contraseña
const modoRecuperacion = ref(false)
const correoRecuperacion = ref('')
const mensajeRecuperacion = ref('')

const recuperar = () => {
  mensajeRecuperacion.value =
    `Si existe una cuenta asociada a ${correoRecuperacion.value}, recibirás un enlace para restablecer tu contraseña.`
}

// RNF-02.1/02.3 — Login real contra el backend (hash bcrypt + JWT)
const ingresar = async () => {
  error.value = ''
  cargando.value = true
  try {
    const resp = await fetch(`${import.meta.env.VITE_API_BIOAGRO_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })
    if (!resp.ok) throw new Error('credenciales')
    const data = await resp.json()
    emit('login', data) // { token, email, rol, cooperativaId }
  } catch {
    error.value = 'Correo o contraseña incorrectos.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <section class="login">
    <div class="login__card">
      <div class="login__brand">
        <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
          <path d="M14 2C14 2 8 8 8 14c0 3.3 2.7 6 6 6s6-2.7 6-6c0-6-6-12-6-12z" fill="#52B788"/>
          <path d="M14 8C14 8 10 12 10 15c0 2.2 1.8 4 4 4s4-1.8 4-4c0-3-4-7-4-7z" fill="#95D5B2"/>
        </svg>
        <span>AgriVision</span>
      </div>
      <h1 class="login__titulo">Iniciar sesión</h1>
      <p class="login__sub">Ingresa tus credenciales para acceder a tu cuenta</p>

      <form v-if="modoRecuperacion" class="login__form" @submit.prevent="recuperar">
        <label>
          Correo de tu cuenta
          <input v-model="correoRecuperacion" type="email" required placeholder="usuario@bioagro.cr" />
        </label>
        <p v-if="mensajeRecuperacion" class="login__ok">{{ mensajeRecuperacion }}</p>
        <button type="submit" class="btn-login">Enviar enlace de recuperación</button>
        <button type="button" class="btn-volver" @click="modoRecuperacion = false; mensajeRecuperacion = ''">← Volver al inicio de sesión</button>
      </form>

      <form v-else class="login__form" @submit.prevent="ingresar">
        <label>
          Correo electrónico
          <input v-model="email" type="email" required placeholder="usuario@bioagro.cr" />
        </label>
        <label>
          Contraseña
          <input v-model="password" type="password" required placeholder="••••••••" />
        </label>
        <p v-if="error" class="login__error">{{ error }}</p>
        <button type="submit" class="btn-login" :disabled="cargando">{{ cargando ? 'Ingresando…' : 'Ingresar' }}</button>
        <button type="button" class="btn-link" @click="modoRecuperacion = true">¿Olvidaste tu contraseña?</button>
        <button type="button" class="btn-volver" @click="$emit('volver')">← Volver al inicio</button>
      </form>

      <div class="login__hint">
        <strong>Demo:</strong> admin@bioagro.cr / admin123 · coop@bioagro.cr / coop123 · tecnico@bioagro.cr / tecnico123
      </div>
    </div>
  </section>
</template>

<style scoped>
.login {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: #F7F5F0;
  font-family: 'Inter', sans-serif;
}

.login__card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 10px 40px rgba(45, 27, 14, 0.08);
}

.login__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'DM Serif Display', serif;
  font-size: 22px;
  margin-bottom: 24px;
}

.login__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: 32px;
}

.login__sub { color: #8a7a6a; margin-bottom: 20px; }

.login__form { display: flex; flex-direction: column; gap: 14px; }

.login__form label { font-size: 13px; font-weight: 500; display: flex; flex-direction: column; gap: 6px; }

.login__form input {
  border: 1px solid #ddd3c4;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
}

.login__form input:focus { outline: none; border-color: #52B788; }

.login__error { color: #c0392b; font-size: 13px; }

.login__ok { color: #2d7a4f; font-size: 13px; background: #e6f6ec; padding: 10px; border-radius: 10px; }

.btn-link { background: none; border: none; color: #52B788; font-size: 13px; text-align: center; }
.btn-link:hover { text-decoration: underline; }

.btn-login {
  background: #2D1B0E;
  color: #F7F5F0;
  border: none;
  border-radius: 999px;
  padding: 12px;
  font-size: 15px;
  font-weight: 500;
  margin-top: 4px;
}

.btn-login:hover { background: #52B788; }

.btn-volver {
  background: transparent;
  border: none;
  color: #8a7a6a;
  font-size: 13px;
  text-align: center;
}

.btn-volver:hover { color: #52B788; }

.login__hint {
  margin-top: 20px;
  font-size: 11px;
  color: #8a7a6a;
  text-align: center;
}
</style>
