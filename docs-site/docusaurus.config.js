// @ts-check

/** AgriVision Docs: mismo GitHub Pages que la landing, subruta /docs/.
 *  La landing vive en /hackathon-5g-2026/ ; este sitio en /hackathon-5g-2026/docs/ .
 */
const config = {
  title: 'AgriVision Docs',
  tagline: 'Detección de broca del café: documentación técnica',
  url: 'https://vertivolatam.github.io',
  baseUrl: '/hackathon-5g-2026/docs/',

  organizationName: 'vertivolatam',
  projectName: 'hackathon-5g-2026',

  onBrokenLinks: 'throw',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'es',
    locales: ['es'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.js',
          // Docs como homepage del subsitio (sin landing page separada).
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'AgriVision Docs',
      // URLs absolutas a propósito: Docusaurus antepone baseUrl a los href
      // relativos y rompería estos links (además, static/api/ no existe en
      // su tabla de rutas y el checker la marcaría rota).
      items: [
        { href: 'https://vertivolatam.github.io/hackathon-5g-2026/', label: 'Landing', position: 'right' },
        { href: 'https://vertivolatam.github.io/hackathon-5g-2026/docs/api/', label: 'API', position: 'right' },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `AgriVision · Hackatón Vertivo · ${new Date().getFullYear()}`,
    },
  },
};

module.exports = config;
