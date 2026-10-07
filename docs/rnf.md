# Requerimientos No Funcionales — BioAgro

| RNF | Estado | Decisión / implementación |
|---|---|---|
| RNF-01.1 (páginas < 3 s) | Parcial | Build de producción con Vite; SPA sin llamadas bloqueantes. Medición real requiere hosting. |
| RNF-01.2 (mapa < 4 s, 100 fincas) | Parcial | Leaflet renderiza polígonos en canvas/SVG liviano; límite real depende del dispositivo y red. |
| RNF-01.3 (correos ≤ 2 min) | Cumplido (arquitectura) | El servicio de correo dispara de inmediato al evento; en producción debe usar cola de jobs (p. ej. BullMQ) con SLA de 2 min. |
| RNF-02.1 (hash de contraseñas) | Pendiente backend | Las credenciales actuales son mock en frontend. Al existir backend: bcrypt/argon2. |
| RNF-02.2 (HTTPS) | Infraestructura | Debe configurarse en el reverse proxy/hosting (certificado TLS). No aplica en dev local. |
| RNF-02.3 (RBAC) | Cumplido a nivel UI | Cada rol ve solo sus vistas y datos (coooperativa → fincas/técnicos/visitas propios, técnico → sus visitas, admin → todo). El backend deberá reforzarlo con verificación de sesión. |
| RNF-02.4 (expiración 60 min) | Cumplido | Temporizador de inactividad de 60 min en `App.vue` (antes 15 min). |
| RNF-02.5 (privacidad de datos) | Política | Manejo vía variables de entorno y sin exponer datos de otras cooperativas en la UI; formalizar con política de privacidad y minimización de datos. |
| RNF-03.1 (responsivo) | Cumplido | Media queries ≤768px: topbar apilada, grids a una columna, tablas con scroll horizontal. |
| RNF-03.2 (colores consistentes) | Cumplido | Variables CSS `--color-prioridad-*` en `App.vue` usadas en badges de toda la plataforma; mapas con el mismo rojo/ámbar/verde. |
| RNF-03.3 (mapa intuitivo) | Cumplido | Zoom con controles de Leaflet, trazado por clics o coordenadas manuales, tooltips de sensores. |
| RNF-04.1 (99% disponibilidad) | Infraestructura | Requiere hosting con balanceo/monitoreo; fuera del alcance del código. |
| RNF-04.2 (último dato disponible) | Cumplido | `bioagroApi.js` devuelve caché + fecha/hora de última actualización y el dashboard muestra aviso de desconexión. |
| RNF-04.3 (reintento de correos) | Cumplido | `correoService.js`: hasta 3 intentos con espera incremental y registro del estado en notificaciones. |
| RNF-05.1 (nuevas cooperativas sin cambios estructurales) | Cumplido | Store reactivo de cooperativas; alta desde la UI de administración. |
| RNF-05.2 (múltiples tipos de sensores) | Cumplido (modelo) | Objetos de sensor con campos extensibles (`nombre`, `lat`, `lng`, `activo`); agregar `tipo`/`unidad` no rompe el modelo. |
| RNF-05.3 (API desacoplada mock → real) | Cumplido | Servicios en `src/services/` (`bioagroApi`, `correoService`, `mapaService`); solo se cambia la implementación interna para apuntar a la API real. |
| RNF-06.1 (arquitectura en capas) | Parcial | Frontend organizado en components/stores/services; backend y BD pendientes. |
| RNF-06.2 (integraciones abstraídas) | Cumplido | `src/services/` aísla mapas, correo y API BioAgro. |
| RNF-06.3 (variables de entorno) | Cumplido | `.env` con `VITE_API_BIOAGRO_URL`, `VITE_MAP_TILES_URL`, `VITE_CORREO_FROM`; consumidas vía `import.meta.env`. |
