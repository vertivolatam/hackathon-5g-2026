# docs-site — BioTrap Docs (Docusaurus)

Subsitio en el mismo GitHub Pages que la landing:

- Landing: `https://vertivolatam.github.io/hackathon-5g-2026/`
- Docs: `https://vertivolatam.github.io/hackathon-5g-2026/docs/`
- API interactiva: `.../docs/api/` (Redoc, generada en CI)

## Desarrollo local

```bash
cd docs-site
npm install
npm start  # http://localhost:3000/hackathon-5g-2026/docs/
```

La página `/api/` no existe en local salvo que la generes:

```bash
python3 ../backend/scripts/export_openapi.py > /tmp/openapi.json  # requiere fastapi+paho
npx -y @redocly/cli@1 build-docs /tmp/openapi.json -o static/api/index.html
```

`static/api/` está en `.gitignore`: se genera en cada build de CI.

## Estructura Diátaxis

`tutorials/` (aprender) · `how-to/` (tareas) · `reference/` (contratos) · `explanation/` (porqués).
Ver `docs/explanation/diataxis.md`.
