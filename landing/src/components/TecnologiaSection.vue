<template>
  <section class="tecnologia" id="tecnologia">
    <div class="tec__inner">
      <div class="tec__header">
        <h2 class="tec__titulo">La tecnología detrás</h2>
        <p class="tec__bajada">Cada componente fue elegido para funcionar en condiciones reales de finca, no solo en laboratorio.</p>
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
  { icono: '📡', titulo: 'Conectividad 5G', desc: 'Transmisión de datos en tiempo real desde zonas rurales. Latencia menor a 10ms para alertas inmediatas.' },
  { icono: '🧠', titulo: 'Edge Computing', desc: 'Procesamiento local en el nodo de campo. La IA corre donde están los datos, sin depender de la nube.' },
  { icono: '🤖', titulo: 'Visión por computadora', desc: 'Modelos de detección entrenados con miles de imágenes de plagas del café costarricense.' },
  { icono: '🌐', titulo: 'IoT agrícola', desc: 'Red de sensores de bajo consumo energético, alimentados por paneles solares en el campo.' },
  { icono: '☁️', titulo: 'Plataforma web', desc: 'Dashboard accesible desde cualquier dispositivo. Mapa de calor, historial y recomendaciones de manejo.' },
  { icono: '🔒', titulo: 'Datos seguros', desc: 'Información del productor protegida y almacenada localmente. Sin dependencia de terceros externos.' },
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