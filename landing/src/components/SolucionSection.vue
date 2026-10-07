<script setup>
import { ref } from 'vue'

const pasoActivo = ref(0)

const pasos = [
  {
    num: '01',
    titulo: 'Trampa inteligente',
    subtitulo: 'Detección en campo',
    desc: 'Trampas físicas con cámara integrada y procesamiento Edge/IA capturan imágenes de las plagas. El sistema identifica y cuenta la especie en tiempo real, sin necesidad de conectividad permanente.',
    icono: '🪤',
    color: '#52B788',
  },
  {
    num: '02',
    titulo: 'Sensores IoT',
    subtitulo: 'Contexto ambiental',
    desc: 'Sensores de temperatura, humedad y condiciones del cultivo complementan la detección. Los datos ambientales permiten predecir condiciones favorables para brotes antes de que ocurran.',
    icono: '🌡️',
    color: '#74C69D',
  },
  {
    num: '03',
    titulo: 'Dron de inspección',
    subtitulo: 'Vista aérea del cultivo',
    desc: 'Drones capturan imágenes multiespectrales de la finca para detectar zonas afectadas que no son visibles a nivel del suelo. Complementan las trampas con cobertura amplia.',
    icono: '🚁',
    color: '#95D5B2',
  },
  {
    num: '04',
    titulo: 'Conectividad 5G',
    subtitulo: 'Transmisión en tiempo real',
    desc: 'La red 5G conecta trampas, sensores y drones con el servidor central. Los datos viajan en milisegundos desde zonas rurales del cafetal hasta la plataforma de análisis.',
    icono: '📡',
    color: '#D4A017',
  },
  {
    num: '05',
    titulo: 'Edge Computing + IA',
    subtitulo: 'Procesamiento local inteligente',
    desc: 'El nodo Edge procesa datos localmente, identifica plagas con modelos de IA y envía solo información relevante. Reduce el consumo de datos y garantiza respuesta rápida incluso con conectividad limitada.',
    icono: '🧠',
    color: '#52B788',
  },
  {
    num: '06',
    titulo: 'Mapa y alertas',
    subtitulo: 'Decisión en manos del productor',
    desc: 'La plataforma web muestra un mapa de actividad de plagas por zona, genera alertas tempranas y recomienda acciones específicas. El productor sabe exactamente dónde actuar y cuándo.',
    icono: '🗺️',
    color: '#74C69D',
  },
]
</script>

<template>
  <section class="solucion" id="solucion">
    <div class="solucion__inner">

      <div class="solucion__header">
        <h2 class="solucion__titulo">Cómo funciona AgriVision</h2>
        <p class="solucion__bajada">
          Un sistema integrado que lleva inteligencia artificial y
          conectividad 5G directamente al campo del productor.
        </p>
      </div>

      <!-- FLUJO INTERACTIVO -->
      <div class="flujo">
        <div class="flujo__pasos">
          <button
            v-for="(paso, i) in pasos"
            :key="i"
            class="flujo__paso"
            :class="{ 'flujo__paso--activo': pasoActivo === i }"
            @click="pasoActivo = i"
          >
            <span class="flujo__paso-num">{{ paso.num }}</span>
            <span class="flujo__paso-titulo">{{ paso.titulo }}</span>
          </button>
        </div>

        <div class="flujo__detalle">
          <Transition name="fade" mode="out-in">
            <div :key="pasoActivo" class="flujo__card">
              <div class="flujo__card-icono" :style="{ background: pasos[pasoActivo].color + '22', borderColor: pasos[pasoActivo].color + '44' }">
                <span>{{ pasos[pasoActivo].icono }}</span>
              </div>
              <div class="flujo__card-content">
                <span class="flujo__card-sub">{{ pasos[pasoActivo].subtitulo }}</span>
                <h3 class="flujo__card-titulo">{{ pasos[pasoActivo].titulo }}</h3>
                <p class="flujo__card-desc">{{ pasos[pasoActivo].desc }}</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- ESCALABILIDAD -->
      <div class="escalable">
        <div class="escalable__texto">
          <h3>Diseñado para crecer</h3>
          <p>AgriVision nació pensando en el café costarricense, pero su arquitectura modular permite adaptarlo a cualquier cultivo o sector agrícola donde la detección temprana de plagas marque la diferencia.</p>
        </div>
        <div class="escalable__cultivos">
          <span v-for="c in ['☕ Café', '🍌 Banano', '🥑 Aguacate', '🍊 Cítricos', '🌽 Maíz', '🌿 Palma']" :key="c" class="cultivo-tag">{{ c }}</span>
        </div>
      </div>

    </div>
  </section>
</template>

<style scoped>
.solucion {
  background: #1B4332;
  padding: 6rem 0;
}

.solucion__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 4rem;
}

.solucion__header {
  max-width: 560px;
  margin-bottom: 4rem;
}

.solucion__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(2rem, 3.5vw, 3rem);
  font-weight: 400;
  color: #F7F5F0;
  line-height: 1.2;
  margin-bottom: 1rem;
}

.solucion__bajada {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 300;
  color: rgba(247, 245, 240, 0.7);
  line-height: 1.7;
}

/* FLUJO */
.flujo {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  margin-bottom: 4rem;
  align-items: start;
}

.flujo__pasos {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.flujo__paso {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
}

.flujo__paso:hover {
  background: rgba(82, 183, 136, 0.1);
}

.flujo__paso--activo {
  background: rgba(82, 183, 136, 0.15) !important;
  border-left: 3px solid #52B788;
}

.flujo__paso-num {
  font-family: 'DM Serif Display', serif;
  font-size: 1.1rem;
  color: #52B788;
  flex-shrink: 0;
  width: 28px;
}

.flujo__paso-titulo {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 400;
  color: rgba(247, 245, 240, 0.8);
}

.flujo__paso--activo .flujo__paso-titulo {
  color: #F7F5F0;
  font-weight: 500;
}

/* CARD */
.flujo__card {
  background: rgba(247, 245, 240, 0.05);
  border: 1px solid rgba(247, 245, 240, 0.1);
  border-radius: 4px;
  padding: 2.5rem;
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  min-height: 220px;
}

.flujo__card-icono {
  width: 72px;
  height: 72px;
  border-radius: 4px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.flujo__card-content { flex: 1; }

.flujo__card-sub {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 500;
  color: #95D5B2;
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: 0.5rem;
}

.flujo__card-titulo {
  font-family: 'DM Serif Display', serif;
  font-size: 1.6rem;
  font-weight: 400;
  color: #F7F5F0;
  margin-bottom: 1rem;
}

.flujo__card-desc {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 300;
  color: rgba(247, 245, 240, 0.75);
  line-height: 1.7;
}

/* TRANSICIÓN */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ESCALABLE */
.escalable {
  background: rgba(82, 183, 136, 0.08);
  border: 1px solid rgba(82, 183, 136, 0.2);
  border-radius: 4px;
  padding: 2rem 2.5rem;
  display: flex;
  gap: 3rem;
  align-items: center;
}

.escalable__texto { flex: 1; }

.escalable__texto h3 {
  font-family: 'DM Serif Display', serif;
  font-size: 1.3rem;
  font-weight: 400;
  color: #F7F5F0;
  margin-bottom: 0.75rem;
}

.escalable__texto p {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: rgba(247, 245, 240, 0.7);
  line-height: 1.65;
  max-width: 420px;
}

.escalable__cultivos {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-width: 280px;
}

.cultivo-tag {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  background: rgba(82, 183, 136, 0.15);
  border: 1px solid rgba(82, 183, 136, 0.3);
  color: #95D5B2;
  padding: 0.35rem 0.75rem;
  border-radius: 2px;
}

@media (max-width: 900px) {
  .solucion__inner { padding: 0 1.5rem; }
  .flujo { grid-template-columns: 1fr; }
  .flujo__pasos { flex-direction: row; flex-wrap: wrap; }
  .flujo__card { flex-direction: column; }
  .escalable { flex-direction: column; gap: 1.5rem; }
}
</style>