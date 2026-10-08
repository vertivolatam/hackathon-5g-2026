# Landing AgriVision: build Vite + serve estático con nginx.
# Imagen usada por Minikube vía backend/k8s/landing.yaml (make mk-build/mk-load).
FROM node:24-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# build-only evita el type-check (el CI de Pages ya lo corre por separado)
RUN npm run build-only

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
