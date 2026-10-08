<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import HeroSection from './components/HeroSection.vue'
import ProblemaSection from './components/ProblemaSection.vue'
import SolucionSection from './components/SolucionSection.vue'
import TecnologiaSection from './components/TecnologiaSection.vue'
import EquipoContacto from './components/EquipoContacto.vue'
import LoginView from './components/LoginView.vue'
import GestionCooperativas from './components/GestionCooperativas.vue'
import DashboardAdmin from './components/DashboardAdmin.vue'
import { cooperativas } from './stores/cooperativas'
import GestionFincas from './components/GestionFincas.vue'
import GestionTecnicos from './components/GestionTecnicos.vue'
import GestionVisitas from './components/GestionVisitas.vue'
import BoletinIncidencias from './components/BoletinIncidencias.vue'
import ReportesCampo from './components/ReportesCampo.vue'
import FooterSection from './components/FooterSection.vue'
import PanelTecnico from './components/PanelTecnico.vue'
import PanelCampoTecnico from './components/PanelCampoTecnico.vue'

const sesionGuardada = localStorage.getItem('bioagro_sesion')
const sesion = ref(sesionGuardada ? JSON.parse(sesionGuardada) : null)
const mostrandoLogin = ref(false)

const nombresRol = {
  administrador: 'Administrador',
  cooperativa: 'Cooperativa',
  tecnico: 'Técnico',
}

const permisosPorRol = {
  administrador: ['Gestionar usuarios', 'Ver todas las cooperativas', 'Configurar la plataforma'],
  cooperativa: ['Ver fincas asignadas', 'Asignar técnicos a visitas', 'Ver reportes de campo'],
  tecnico: ['Ver mis visitas programadas', 'Registrar monitoreos en campo', 'Subir evidencias de plagas'],
}

const onLogin = (data) => {
  sesion.value = data
  localStorage.setItem('bioagro_sesion', JSON.stringify(data))
  mostrandoLogin.value = false
  programarExpiracion()
}

const salir = () => {
  sesion.value = null
  localStorage.removeItem('bioagro_sesion')
  limpiarTemporizador()
}

// RF-02.4 — Expiración automática por inactividad (15 min)
const MINUTOS_INACTIVIDAD = 60
let temporizador = null

const expirarSesion = () => {
  if (sesion.value) {
    salir()
    alert('Tu sesión expiró por inactividad.')
  }
}

const limpiarTemporizador = () => {
  if (temporizador) clearTimeout(temporizador)
  temporizador = null
}

const programarExpiracion = () => {
  limpiarTemporizador()
  if (sesion.value) {
    temporizador = setTimeout(expirarSesion, MINUTOS_INACTIVIDAD * 60 * 1000)
  }
}

const alActividad = () => programarExpiracion()

onMounted(() => {
  ['mousemove', 'keydown', 'click', 'scroll'].forEach((evento) =>
    window.addEventListener(evento, alActividad),
  )
  programarExpiracion()
})

onUnmounted(() => {
  limpiarTemporizador()
  ;['mousemove', 'keydown', 'click', 'scroll'].forEach((evento) =>
    window.removeEventListener(evento, alActividad),
  )
})

// RF-02.2 — Cada cooperativa solo ve su propia información
const esCooperativa = computed(() => sesion.value?.rol === 'cooperativa')

const cooperativaActualId = computed(() => sesion.value?.cooperativaId || 'coop-1')

const miCooperativa = computed(() =>
  esCooperativa.value ? cooperativas.find((c) => c.id === cooperativaActualId.value) : null,
)
</script>

<template>
  <div id="App">
    <header class="topbar">
      <span class="topbar__marca">AgriVision</span>
      <nav class="topbar__acciones" v-if="sesion">
        <span class="topbar__sesion">{{ sesion.email }} · <strong>{{ nombresRol[sesion.rol] }}</strong></span>
        <button class="topbar__salir" @click="salir">Cerrar sesión</button>
      </nav>
      <button v-else class="topbar__login" @click="mostrandoLogin = !mostrandoLogin">
        Iniciar sesión
      </button>
    </header>

    <LoginView v-if="mostrandoLogin && !sesion" @login="onLogin" @volver="mostrandoLogin = false" />

    <template v-else>
      <section v-if="sesion" class="panel-rol">
        <h2>Bienvenido, {{ nombresRol[sesion.rol] }}</h2>
        <p>Tienes acceso a:</p>
        <ul>
          <li v-for="permiso in permisosPorRol[sesion.rol]" :key="permiso">{{ permiso }}</li>
        </ul>
      </section>

      <GestionCooperativas v-if="sesion && sesion.rol === 'administrador'" />
      <DashboardAdmin v-if="sesion && sesion.rol === 'administrador'" />

      <!-- RF-02.2 — Panel exclusivo de la cooperativa autenticada (siempre visible para el rol) -->
      <section v-if="esCooperativa" class="panel-rol">
        <h2 v-if="miCooperativa">Mi cooperativa: {{ miCooperativa.nombre }}</h2>
        <h2 v-else>Panel de cooperativa</h2>
        <p v-if="miCooperativa"><strong>Región:</strong> {{ miCooperativa.region }} · <strong>Contacto:</strong> {{ miCooperativa.correo }} · <strong>Estado:</strong> {{ miCooperativa.activa ? 'Activa' : 'Inactiva' }}</p>
        <p v-else>Aún no hay una cooperativa registrada con este usuario. Pide al administrador que la registre, o usa las secciones de abajo para agregar fincas y técnicos.</p>
      </section>

      <GestionFincas v-if="esCooperativa" :cooperativaId="cooperativaActualId" />
      <GestionTecnicos v-if="esCooperativa" :cooperativaId="cooperativaActualId" />
      <GestionVisitas v-if="esCooperativa" :cooperativaId="cooperativaActualId" />
      <BoletinIncidencias v-if="esCooperativa" :cooperativaId="cooperativaActualId" />
      <ReportesCampo v-if="esCooperativa" :cooperativaId="cooperativaActualId" />

      <PanelTecnico v-if="sesion && sesion.rol === 'tecnico'" :email="sesion.email" />
      <PanelCampoTecnico v-if="sesion && sesion.rol === 'tecnico'" :email="sesion.email" />

      <!-- Landing page solo visible cuando NO hay sesión -->
      <template v-if="!sesion">
        <HeroSection />
        <ProblemaSection />
        <SolucionSection />
        <TecnologiaSection />
        <EquipoContacto />
      </template>

      <FooterSection />
    </template>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html { scroll-behavior: smooth; }

:root {
  /* RNF-03.2 — colores consistentes de prioridad en toda la plataforma */
  --color-prioridad-alta: #c0392b;
  --color-prioridad-seguimiento: #f39c12;
  --color-prioridad-ok: #2d7a4f;
  --color-prioridad-alta-bg: #fdecea;
  --color-prioridad-seguimiento-bg: #fff3cd;
  --color-prioridad-ok-bg: #e6f6ec;
}

body {
  background: #F7F5F0;
  color: #2D1B0E;
  -webkit-font-smoothing: antialiased;
}

#app { min-height: 100vh; }

img { max-width: 100%; display: block; }
a { text-decoration: none; color: inherit; }
button { cursor: pointer; }

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #2D1B0E;
  color: #F7F5F0;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
}

.topbar__marca {
  font-family: 'DM Serif Display', serif;
  font-size: 20px;
}

.topbar__acciones {
  display: flex;
  align-items: center;
  gap: 16px;
}

.topbar__login,
.topbar__salir {
  background: transparent;
  border: 1px solid #52B788;
  color: #52B788;
  border-radius: 999px;
  padding: 6px 16px;
  font-size: 13px;
}

.topbar__login:hover,
.topbar__salir:hover { background: #52B788; color: #2D1B0E; }

.panel-rol {
  font-family: 'Inter', sans-serif;
  background: #fff;
  border-bottom: 1px solid #ece5d8;
  padding: 24px;
}

.panel-rol h2 {
  font-family: 'DM Serif Display', serif;
  margin-bottom: 8px;
}

.panel-rol ul { margin: 8px 0 0 20px; }
.panel-rol li { margin-bottom: 4px; }

/* RNF-03.1 — Diseño responsivo para celulares */
@media (max-width: 768px) {
  .topbar { flex-direction: column; gap: 8px; align-items: stretch; }
  .topbar__acciones { justify-content: space-between; }
  .panel-rol { padding: 16px; }
  .fincas__layout,
  .graficos,
  .graficos--2 { grid-template-columns: 1fr !important; }
  .tabla { display: block; overflow-x: auto; }
  .tarjetas { flex-direction: column; }
  .dashboard__grid { flex-direction: column; }
  .filtros { flex-wrap: wrap; }
}
</style>
