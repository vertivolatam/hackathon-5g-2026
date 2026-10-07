<script setup>
import HeroSection from './components/HeroSection.vue'
import ProblemaSection from './components/ProblemaSection.vue'
import SolucionSection from './components/SolucionSection.vue'
import TecnologiaSection from './components/TecnologiaSection.vue'
import EquipoContacto from './components/EquipoContacto.vue'
</script>

<template>
  <div id="App">
    <HeroSection />
    <ProblemaSection />
    <SolucionSection />
    <TecnologiaSection />
    <EquipoContacto />
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

body {
  background: #F7F5F0;
  color: #2D1B0E;
  -webkit-font-smoothing: antialiased;
}

#app { min-height: 100vh; }

img { max-width: 100%; display: block; }
a { text-decoration: none; color: inherit; }
button { cursor: pointer; }
</style>