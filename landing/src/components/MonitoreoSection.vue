<template>
  <section class="monitoreo" id="monitoreo">
    <div class="monitoreo__inner">
      <div class="monitoreo__header">
        <h2 class="monitoreo__titulo">Monitoreo en vivo</h2>
        <p class="monitoreo__bajada">
          Panel de Grafana incrustado en esta página (detecciones de la última campaña).
          Si ves el mensaje de configuración, levanta el stack con <code>make dev-full</code>.
        </p>
      </div>
      <GrafanaEmbed title="Detecciones AgriVision" :panel-id="1" />
    </div>
  </section>
</template>

<script setup>
import GrafanaEmbed from './GrafanaEmbed.vue'
</script>

<style scoped>
.monitoreo {
  background: white;
  padding: 6rem 0;
  border-top: 1px solid #e8e4dd;
}
.monitoreo__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 4rem;
}
.monitoreo__header {
  max-width: 520px;
  margin-bottom: 2.5rem;
}
.monitoreo__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  font-weight: 400;
  color: #1b4332;
  margin-bottom: 1rem;
}
.monitoreo__bajada {
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 300;
  color: #4a5568;
  line-height: 1.7;
}
.monitoreo__bajada code {
  font-size: 13px;
  background: #f7f5f0;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
}
</style>
