<template>
  <footer class="footer">
    <div class="footer__brand">
      <svg width="20" height="20" viewBox="0 0 28 28" fill="none">
        <path d="M14 2C14 2 8 8 8 14c0 3.3 2.7 6 6 6s6-2.7 6-6c0-6-6-12-6-12z" fill="#52B788"/>
        <path d="M14 8C14 8 10 12 10 15c0 2.2 1.8 4 4 4s4-1.8 4-4c0-3-4-7-4-7z" fill="#95D5B2"/>
      </svg>
      <span>AgriVision · Vertivo · 2026</span>
    </div>
    <p>Monitoreo agrícola · Costa Rica</p>
  </footer>
</template>

<style scoped>
.footer {
  background: #2D1B0E;
  padding: 2rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer__brand { display: flex; align-items: center; gap: 8px; }
.footer__brand span { font-family: 'DM Serif Display', serif; font-size: 14px; color: rgba(247, 245, 240, 0.6); }
.footer p { font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(247, 245, 240, 0.4); }

@media (max-width: 900px) {
  .footer { flex-direction: column; gap: 0.5rem; padding: 1.5rem; text-align: center; }
}
</style>
