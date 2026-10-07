<template>
  <section class="problema" id="problema">
    <div class="problema__inner">

      <div class="problema__header">
        <h2 class="problema__titulo">El café costarricense<br>enfrenta un enemigo silencioso.</h2>
        <p class="problema__bajada">
          Las plagas se detectan cuando el daño ya está hecho. El productor
          pierde tiempo, dinero y cosecha por falta de información oportuna.
        </p>
      </div>

      <div class="problema__plagas">

        <div class="plaga-card">
          <div class="plaga-card__img plaga-card__img--roya">
            <span class="plaga-card__icon">🍂</span>
          </div>
          <div class="plaga-card__body">
            <span class="plaga-card__nivel roya">Amenaza crítica</span>
            <h3>Roya del café</h3>
            <p class="plaga-card__nombre-cientifico">Hemileia vastatrix</p>
            <p>Hongo que destruye las hojas del cafeto, impidiendo la fotosíntesis y
            reduciendo drásticamente la producción. Se propaga rápidamente en
            condiciones de alta humedad.</p>
            <div class="plaga-card__dato">
              <span class="dato-num">70%</span>
              <span class="dato-desc">de pérdida de cosecha en brotes severos sin detección temprana</span>
            </div>
          </div>
        </div>

        <div class="plaga-card">
          <div class="plaga-card__img plaga-card__img--minador">
            <span class="plaga-card__icon">🐛</span>
          </div>
          <div class="plaga-card__body">
            <span class="plaga-card__nivel minador">Amenaza alta</span>
            <h3>Minador de la hoja</h3>
            <p class="plaga-card__nombre-cientifico">Leucoptera coffeella</p>
            <p>Larva que excava galerías dentro de las hojas del café. Su presencia
            pasa desapercibida hasta que el daño foliar es extenso y la planta
            ya perdió capacidad productiva.</p>
            <div class="plaga-card__dato">
              <span class="dato-num">35%</span>
              <span class="dato-desc">de reducción en rendimiento cuando el ataque no es detectado a tiempo</span>
            </div>
          </div>
        </div>

        <div class="plaga-card">
          <div class="plaga-card__img plaga-card__img--broca">
            <span class="plaga-card__icon">🪲</span>
          </div>
          <div class="plaga-card__body">
            <span class="plaga-card__nivel broca">Amenaza alta</span>
            <h3>Broca del café</h3>
            <p class="plaga-card__nombre-cientifico">Hypothenemus hampei</p>
            <p>Insecto que perfora el grano de café y se reproduce en su interior,
            afectando directamente la calidad del producto final y su valor
            en el mercado internacional.</p>
            <div class="plaga-card__dato">
              <span class="dato-num">40%</span>
              <span class="dato-desc">de los granos afectados pierden su valor comercial</span>
            </div>
          </div>
        </div>

      </div>

      <div class="problema__contexto">
        <div class="ctx-item">
          <span class="ctx-item__icon">📍</span>
          <p>Costa Rica produce más de <strong>90,000 toneladas</strong> de café al año. Las plagas amenazan directamente la economía de miles de familias productoras.</p>
        </div>
        <div class="ctx-item">
          <span class="ctx-item__icon">⏱</span>
          <p>La detección tradicional depende de inspecciones visuales manuales, que ocurren cada <strong>2 a 4 semanas</strong>. Para entonces, el daño ya es extenso.</p>
        </div>
        <div class="ctx-item">
          <span class="ctx-item__icon">📡</span>
          <p>Las zonas cafetaleras de Costa Rica tienen cobertura 5G emergente, pero <strong>ningún sistema actual</strong> la aprovecha para monitoreo agrícola en tiempo real.</p>
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

.plaga-card__img--roya    { background: linear-gradient(135deg, #744210, #B7791F); }
.plaga-card__img--minador { background: linear-gradient(135deg, #276749, #38A169); }
.plaga-card__img--broca   { background: linear-gradient(135deg, #1B4332, #2D6A4F); }

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

.roya    { background: #FEF3C7; color: #92400E; }
.minador { background: #D1FAE5; color: #065F46; }
.broca   { background: #ECFDF5; color: #1B4332; }

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