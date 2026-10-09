<template>
  <section class="tecnologia" id="tecnologia">
    <div class="tec__inner">
      <div class="tec__header">
        <h2 class="tec__titulo">La arquitectura detrás</h2>
        <p class="tec__bajada">Cada componente fue elegido para funcionar en condiciones reales
        de finca y cooperativa, no solo en laboratorio.</p>
      </div>

      <div class="tec__grid">
        <div class="tec-item" v-for="tec in tecnologias" :key="tec.titulo">
          <div class="tec-item__icono">{{ tec.icono }}</div>
          <h4>{{ tec.titulo }}</h4>
          <p>{{ tec.desc }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const tecnologias = [
  { icono: '📡', titulo: 'Conectividad 5G', desc:'AgriVision aprovecha 5G Standalone para conectar múltiples nodos distribuidos. Transmisión de imágenes bajo demanda, baja latencia y arquitectura que escala junto con Edge e IoT.' },
  { icono: '🧠', titulo: 'Edge Computing', desc: 'Procesamiento local en campo. La IA corre donde están los datos, reduciendo el volumen transmitido y garantizando respuesta rápida incluso con conectividad intermitente.' },
  { icono: '📶', titulo: 'LoRaWAN + Gateway', desc: 'Infraestructura actual para sensores de temperatura, humedad, estaciones meteorológicas y sensores de suelo. Largo alcance y bajo consumo energético en zonas rurales.' },
  { icono: '🤖', titulo: 'IA y visión por computadora', desc: 'Modelos entrenados para identificar plagas y condiciones de riesgo a partir de imágenes de trampas, cámaras y drones. La IA genera el evento que alimenta la priorización de AgriVision.' },
  { icono: '☁️', titulo: 'Plataforma AgriVision', desc: 'Dashboard web y app móvil accesibles para el técnico. Semáforo de priorización, historial por finca, alertas y recomendaciones. Base de datos, broker MQTT, API y webhooks en la nube.' },
  { icono: '🔒', titulo: 'Arquitectura modular', desc: 'Cada fuente de datos (trampa, sensor, cámara, satélite, historial) es un módulo independiente. Se agregan o reemplazan sin rediseñar la plataforma completa.' },
]
</script>

<style scoped>
.tecnologia {
  background: #F7F5F0;
  padding: 6rem 0;
}

.tec__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 4rem;
}

.tec__header {
  max-width: 520px;
  margin-bottom: 3.5rem;
}

.tec__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  font-weight: 400;
  color: #1B4332;
  margin-bottom: 1rem;
}

.tec__bajada {
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 300;
  color: #4A5568;
  line-height: 1.7;
}

.tec__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.tec-item {
  background: white;
  border: 1px solid #E8E4DD;
  border-radius: 4px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: border-color 0.2s;
}

.tec-item:hover { border-color: #52B788; }

.tec-item__icono { font-size: 2rem; }

.tec-item h4 {
  font-family: 'DM Serif Display', serif;
  font-size: 1.15rem;
  font-weight: 400;
  color: #1B4332;
}

.tec-item p {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: #4A5568;
  line-height: 1.65;
}

@media (max-width: 900px) {
  .tec__inner { padding: 0 1.5rem; }
  .tec__grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 600px) {
  .tec__grid { grid-template-columns: 1fr; }
}
</style>