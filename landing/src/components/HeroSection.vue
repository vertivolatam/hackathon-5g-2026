<script setup>
const scrollTo = (id) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <section class="hero">
    <div class="hero__overlay"></div>
    <nav class="nav">
      <div class="nav__brand">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <path d="M14 2C14 2 8 8 8 14c0 3.3 2.7 6 6 6s6-2.7 6-6c0-6-6-12-6-12z" fill="#52B788"/>
          <path d="M14 8C14 8 10 12 10 15c0 2.2 1.8 4 4 4s4-1.8 4-4c0-3-4-7-4-7z" fill="#95D5B2"/>
        </svg>
        <span class="nav__name">AgriVision</span>
      </div>
      <div class="nav__links">
        <a @click="scrollTo('problema')">Problema</a>
        <a @click="scrollTo('solucion')">Solución</a>
        <a @click="scrollTo('tecnologia')">Tecnología</a>
        <a @click="scrollTo('equipo')">Equipo</a>
        <a href="/hackathon-5g-2026/docs/">Docs</a>
        <a @click="scrollTo('contacto')" class="nav__cta">Contáctenos</a>
      </div>
    </nav>

    <div class="hero__content">
      <div class="hero__tag">Hackatón Vertivo 2025 · Costa Rica</div>
      <h1 class="hero__title">
        Detectamos plagas<br>
        <em>antes de que destruyan</em><br>
        su cosecha.
      </h1>
      <p class="hero__desc">
        AgriVision combina trampas inteligentes, sensores IoT y tecnología 5G
        para que los productores de café de Costa Rica actúen a tiempo,
        no después de la pérdida.
      </p>
      <div class="hero__actions">
        <button @click="scrollTo('solucion')" class="btn-primary">Ver cómo funciona</button>
        <button @click="scrollTo('problema')" class="btn-ghost">El problema</button>
      </div>
      <div class="hero__stats">
        <div class="stat">
          <span class="stat__num">40%</span>
          <span class="stat__label">pérdida de cosecha por plagas no detectadas a tiempo</span>
        </div>
        <div class="stat__div"></div>
        <div class="stat">
          <span class="stat__num">3</span>
          <span class="stat__label">plagas principales monitoreadas en tiempo real</span>
        </div>
        <div class="stat__div"></div>
        <div class="stat">
          <span class="stat__num">5G</span>
          <span class="stat__label">conectividad de vanguardia en zonas rurales</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  min-height: 100vh;
  background: url('https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1600&q=80') center/cover no-repeat;
  display: flex;
  flex-direction: column;
}

.hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    160deg,
    rgba(27, 67, 50, 0.92) 0%,
    rgba(27, 67, 50, 0.75) 50%,
    rgba(27, 67, 50, 0.55) 100%
  );
}

/* NAV */
.nav {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 4rem;
}

.nav__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.nav__name {
  font-family: 'DM Serif Display', serif;
  font-size: 22px;
  color: #F7F5F0;
  letter-spacing: 0.02em;
}

.nav__links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav__links a {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: rgba(247, 245, 240, 0.8);
  cursor: pointer;
  transition: color 0.2s;
  text-decoration: none;
}

.nav__links a:hover { color: #F7F5F0; }

.nav__cta {
  background: rgba(82, 183, 136, 0.2);
  border: 1px solid rgba(82, 183, 136, 0.5);
  padding: 0.5rem 1.25rem !important;
  border-radius: 2px;
  color: #95D5B2 !important;
  transition: background 0.2s !important;
}

.nav__cta:hover {
  background: rgba(82, 183, 136, 0.35) !important;
}

/* CONTENIDO */
.hero__content {
  position: relative;
  z-index: 10;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2rem 4rem 5rem;
  max-width: 760px;
}

.hero__tag {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 500;
  color: #95D5B2;
  letter-spacing: 0.08em;
  margin-bottom: 1.5rem;
  padding: 0.35rem 0.875rem;
  border: 1px solid rgba(149, 213, 178, 0.4);
  display: inline-block;
  width: fit-content;
  border-radius: 2px;
}

.hero__title {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(2.8rem, 5vw, 4.2rem);
  font-weight: 400;
  line-height: 1.1;
  color: #F7F5F0;
  margin-bottom: 1.5rem;
}

.hero__title em {
  font-style: italic;
  color: #95D5B2;
}

.hero__desc {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 300;
  line-height: 1.7;
  color: rgba(247, 245, 240, 0.8);
  max-width: 520px;
  margin-bottom: 2.5rem;
}

.hero__actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 4rem;
  flex-wrap: wrap;
}

.btn-primary {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  background: #52B788;
  color: #1B4332;
  border: none;
  padding: 0.875rem 2rem;
  cursor: pointer;
  border-radius: 2px;
  transition: background 0.2s;
}

.btn-primary:hover { background: #74C69D; }

.btn-ghost {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  background: transparent;
  color: #F7F5F0;
  border: 1px solid rgba(247, 245, 240, 0.4);
  padding: 0.875rem 2rem;
  cursor: pointer;
  border-radius: 2px;
  transition: border-color 0.2s;
}

.btn-ghost:hover { border-color: rgba(247, 245, 240, 0.8); }

/* STATS */
.hero__stats {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat { display: flex; flex-direction: column; gap: 4px; }

.stat__num {
  font-family: 'DM Serif Display', serif;
  font-size: 2.25rem;
  color: #D4A017;
  line-height: 1;
}

.stat__label {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 300;
  color: rgba(247, 245, 240, 0.65);
  max-width: 140px;
  line-height: 1.4;
}

.stat__div {
  width: 1px;
  height: 48px;
  background: rgba(247, 245, 240, 0.2);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .nav { padding: 1.25rem 1.5rem; }
  .nav__links { display: none; }
  .hero__content { padding: 2rem 1.5rem 4rem; }
  .hero__title { font-size: 2.4rem; }
  .stat__div { display: none; }
}
</style>