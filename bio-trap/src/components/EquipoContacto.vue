<script setup>
import { ref } from 'vue'

const miembros = [
  { nombre: 'Equipo Vertivo', rol: 'Desarrollo & Innovación', inicial: 'V' },
  { nombre: 'Integrante 1', rol: 'Rol del integrante', inicial: '?' },
  { nombre: 'Integrante 2', rol: 'Rol del integrante', inicial: '?' },
  { nombre: 'Integrante 3', rol: 'Rol del integrante', inicial: '?' },
]

const form = ref({ nombre: '', correo: '', mensaje: '' })
const enviado = ref(false)
const error = ref('')

const enviar = () => {
  error.value = ''
  if (!form.value.nombre || !form.value.correo || !form.value.mensaje) {
    error.value = 'Por favor completá todos los campos.'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.correo)) {
    error.value = 'El correo ingresado no es válido.'
    return
  }
  enviado.value = true
}
</script>

<template>
  <!-- EQUIPO -->
  <section class="equipo" id="equipo">
    <div class="equipo__inner">
      <h2 class="equipo__titulo">El equipo</h2>
      <p class="equipo__bajada">Vertivo — un grupo multidisciplinario comprometido con transformar la agricultura costarricense con tecnología accesible.</p>

      <div class="equipo__grid">
        <div class="miembro" v-for="m in miembros" :key="m.nombre">
          <div class="miembro__avatar">{{ m.inicial }}</div>
          <h4>{{ m.nombre }}</h4>
          <span>{{ m.rol }}</span>
        </div>
      </div>
    </div>
  </section>

  <!-- CONTACTO -->
  <section class="contacto" id="contacto">
    <div class="contacto__inner">
      <div class="contacto__texto">
        <h2 class="contacto__titulo">¿Le interesa BioTrap para su finca?</h2>
        <p>Estamos en etapa de prototipo y buscamos productores y aliados para la prueba piloto. Escríbanos y nos ponemos en contacto.</p>
        <div class="contacto__datos">
          <span>📧 contacto@biotrap.cr</span>
          <span>📍 Costa Rica</span>
          <span>🏆 Proyecto Hackatón Vertivo 2025</span>
        </div>
      </div>

      <div class="contacto__form">
        <div v-if="!enviado">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="form.nombre" type="text" placeholder="Su nombre completo">
          </div>
          <div class="form-group">
            <label>Correo electrónico</label>
            <input v-model="form.correo" type="email" placeholder="su@correo.com">
          </div>
          <div class="form-group">
            <label>Mensaje</label>
            <textarea v-model="form.mensaje" rows="4" placeholder="Cuéntenos sobre su finca o interés en BioTrap..."></textarea>
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button @click="enviar" class="btn-enviar">Enviar mensaje</button>
        </div>
        <div v-else class="form-exito">
          <span>✅</span>
          <p>¡Gracias por su interés! El equipo Vertivo se pondrá en contacto pronto.</p>
        </div>
      </div>
    </div>

    <div class="footer">
      <div class="footer__brand">
        <svg width="20" height="20" viewBox="0 0 28 28" fill="none">
          <path d="M14 2C14 2 8 8 8 14c0 3.3 2.7 6 6 6s6-2.7 6-6c0-6-6-12-6-12z" fill="#52B788"/>
          <path d="M14 8C14 8 10 12 10 15c0 2.2 1.8 4 4 4s4-1.8 4-4c0-3-4-7-4-7z" fill="#95D5B2"/>
        </svg>
        <span>BioTrap · Vertivo · 2025</span>
      </div>
      <p>Monitoreo inteligente de plagas del café · Costa Rica</p>
    </div>
  </section>
</template>

<style scoped>
/* EQUIPO */
.equipo {
  background: #F7F5F0;
  padding: 6rem 0;
}

.equipo__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 4rem;
}

.equipo__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  color: #1B4332;
  margin-bottom: 0.75rem;
}

.equipo__bajada {
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 300;
  color: #4A5568;
  line-height: 1.7;
  max-width: 560px;
  margin-bottom: 3rem;
}

.equipo__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.miembro {
  background: white;
  border: 1px solid #E8E4DD;
  border-radius: 4px;
  padding: 2rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.miembro__avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #1B4332;
  color: #95D5B2;
  font-family: 'DM Serif Display', serif;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.miembro h4 {
  font-family: 'DM Serif Display', serif;
  font-size: 1.1rem;
  color: #1B4332;
}

.miembro span {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: #6B7280;
}

/* CONTACTO */
.contacto {
  background: #1B4332;
  padding: 6rem 0 0;
}

.contacto__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 4rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: start;
}

.contacto__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  color: #F7F5F0;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.contacto__texto p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 300;
  color: rgba(247, 245, 240, 0.7);
  line-height: 1.7;
  margin-bottom: 2rem;
}

.contacto__datos {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.contacto__datos span {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #95D5B2;
}

/* FORM */
.contacto__form {
  background: rgba(247, 245, 240, 0.05);
  border: 1px solid rgba(247, 245, 240, 0.1);
  border-radius: 4px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 500;
  color: rgba(247, 245, 240, 0.6);
  letter-spacing: 0.05em;
}

.form-group input,
.form-group textarea {
  background: rgba(247, 245, 240, 0.06);
  border: 1px solid rgba(247, 245, 240, 0.15);
  border-radius: 2px;
  padding: 0.75rem;
  color: #F7F5F0;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  resize: none;
}

.form-group input::placeholder,
.form-group textarea::placeholder { color: rgba(247, 245, 240, 0.3); }

.form-group input:focus,
.form-group textarea:focus { border-color: #52B788; }

.form-error {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: #FCA5A5;
}

.btn-enviar {
  background: #52B788;
  color: #1B4332;
  border: none;
  padding: 0.875rem;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 2px;
  transition: background 0.2s;
  width: 100%;
}

.btn-enviar:hover { background: #74C69D; }

.form-exito {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.form-exito span { font-size: 2.5rem; }

.form-exito p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #95D5B2;
  line-height: 1.6;
}

/* FOOTER */
.footer {
  margin-top: 4rem;
  padding: 2rem 4rem;
  border-top: 1px solid rgba(247, 245, 240, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer__brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer__brand span {
  font-family: 'DM Serif Display', serif;
  font-size: 14px;
  color: rgba(247, 245, 240, 0.6);
}

.footer p {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: rgba(247, 245, 240, 0.4);
}

@media (max-width: 900px) {
  .equipo__inner, .contacto__inner { padding: 0 1.5rem; }
  .equipo__grid { grid-template-columns: repeat(2, 1fr); }
  .contacto__inner { grid-template-columns: 1fr; }
  .footer { flex-direction: column; gap: 0.5rem; padding: 1.5rem; text-align: center; }
}
</style>