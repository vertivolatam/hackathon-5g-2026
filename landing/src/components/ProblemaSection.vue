<template>
  <section class="problema" id="problema">
    <div class="problema__inner">

      <div class="problema__header">
        <h2 class="problema__titulo">Las cooperativas no pueden<br>estar en todas las fincas<br>al mismo tiempo.</h2>
        <p class="problema__bajada">
          El problema no es la falta de datos. Es convertir la información
          disponible en una decisión operativa: ¿dónde debe ir primero el técnico?
        </p>
      </div>

      <div class="problema__plagas">

        <div class="plaga-card">
          <div class="plaga-card__img plaga-card__img--recurso">
            <span class="plaga-card__icon">👥</span>
          </div>
          <div class="plaga-card__body">
            <span class="plaga-card__nivel nivel--recurso">Recurso limitado</span>
            <h3>El técnico no puede estar en todas partes</h3>
            <p>Una cooperativa puede atender decenas o cientos de fincas con
            un equipo técnico reducido. Cada visita tiene un costo y una
            oportunidad. Ir a la finca equivocada es tiempo y dinero perdido.</p>
            <div class="plaga-card__dato">
              <span class="dato-num">60%</span>
              <span class="dato-desc">de las visitas técnicas ocurren sin información actualizada del estado de la finca</span>
            </div>
          </div>
        </div>

        <div class="plaga-card">
          <div class="plaga-card__img plaga-card__img--deteccion">
            <span class="plaga-card__icon">⏰</span>
          </div>
          <div class="plaga-card__body">
            <span class="plaga-card__nivel nivel--deteccion">Detección tardía</span>
            <h3>La información llega cuando el daño ya ocurrió</h3>
            <p>Las inspecciones visuales tradicionales ocurren cada 2 a 4 semanas.
            Para cuando se detecta un brote de broca, roya u otra plaga,
            el daño ya afecta la cosecha y se ha propagado a sectores vecinos.</p>
            <div class="plaga-card__dato">
              <span class="dato-num">40%</span>
              <span class="dato-desc">de pérdida promedio cuando la plaga no se detecta en las primeras 72 horas</span>
            </div>
          </div>
        </div>

        <div class="plaga-card">
          <div class="plaga-card__img plaga-card__img--datos">
            <span class="plaga-card__icon">📊</span>
          </div>
          <div class="plaga-card__body">
            <span class="plaga-card__nivel nivel--datos">Datos sin acción</span>
            <h3>Los datos existen pero no se convierten en decisiones</h3>
            <p>Hay sensores, trampas, imágenes y datos climáticos disponibles.
            El problema es que no están integrados en un sistema que responda
            la pregunta clave del técnico antes de salir a campo.</p>
            <div class="plaga-card__dato">
              <span class="dato-num">10%</span>
              <span class="dato-desc">o menos de los datos agrícolas capturados se convierten en una acción concreta</span>
            </div>
          </div>
        </div>

      </div>

      <div class="problema__contexto">
        <div class="ctx-item">
          <span class="ctx-item__icon">📍</span>
          <p>Costa Rica tiene más de <strong>90,000 productores de café</strong>. Las cooperativas son el puente entre el productor y el mercado, pero operan con recursos técnicos limitados.</p>
        </div>
        <div class="ctx-item">
          <span class="ctx-item__icon">⏱</span>
          <p>El técnico decide a dónde ir con información desactualizada o sin información. <strong>AgriVision cambia eso</strong> con priorización en tiempo real basada en datos del campo.</p>
        </div>
        <div class="ctx-item">
          <span class="ctx-item__icon">📡</span>
          <p>AgriVision integra <strong>múltiples fuentes de datos</strong> — trampas, sensores, cámaras, clima e historial — y las convierte en una prioridad de acción para el equipo técnico.</p>
        </div>
      </div>

    </div>
  </section>
</template>

<style scoped>
.problema {
  background: #F7F5F0;
  padding: 6rem 0;
}

.problema__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 4rem;
}

.problema__header {
  max-width: 680px;
  margin-bottom: 4rem;
}

.problema__titulo {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(2rem, 3.5vw, 3rem);
  font-weight: 400;
  color: #1B4332;
  line-height: 1.2;
  margin-bottom: 1.25rem;
}

.problema__bajada {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 300;
  color: #4A5568;
  line-height: 1.7;
}

/* TARJETAS DE PLAGAS */
.problema__plagas {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 4rem;
}

.plaga-card {
  background: white;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #E8E4DD;
}

.plaga-card__img {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plaga-card__img--recurso   { background: linear-gradient(135deg, #1B4332, #2D6A4F); }
.plaga-card__img--deteccion { background: linear-gradient(135deg, #744210, #B7791F); }
.plaga-card__img--datos     { background: linear-gradient(135deg, #1A365D, #2B6CB0); }

.plaga-card__icon { font-size: 3rem; }

.plaga-card__body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.plaga-card__nivel {
  font-family: 'Inter', sans-serif;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  padding: 0.2rem 0.6rem;
  border-radius: 2px;
  width: fit-content;
}

.nivel--recurso   { background: #ECFDF5; color: #1B4332; }
.nivel--deteccion { background: #FEF3C7; color: #92400E; }
.nivel--datos     { background: #EBF8FF; color: #1A365D; }

.plaga-card__body h3 {
  font-family: 'DM Serif Display', serif;
  font-size: 1.3rem;
  font-weight: 400;
  color: #1B4332;
}

.plaga-card__nombre-cientifico {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-style: italic;
  color: #9CA3AF;
}

.plaga-card__body p {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: #4A5568;
  line-height: 1.65;
}

.plaga-card__dato {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #E8E4DD;
  margin-top: 0.5rem;
}

.dato-num {
  font-family: 'DM Serif Display', serif;
  font-size: 1.75rem;
  color: #D4A017;
  flex-shrink: 0;
}

.dato-desc {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  color: #6B7280;
  line-height: 1.4;
}

/* CONTEXTO */
.problema__contexto {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  background: #1B4332;
  padding: 2.5rem;
  border-radius: 4px;
}

.ctx-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.ctx-item__icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.ctx-item p {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: rgba(247, 245, 240, 0.8);
  line-height: 1.65;
}

.ctx-item p strong {
  color: #95D5B2;
  font-weight: 500;
}

@media (max-width: 900px) {
  .problema__inner { padding: 0 1.5rem; }
  .problema__plagas { grid-template-columns: 1fr; }
  .problema__contexto { grid-template-columns: 1fr; }
}
</style>