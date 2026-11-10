# Shell — se construye y despliega de forma independiente (un contenedor por microfrontend).
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
# El frontend habla con el backend a través del gateway.
ARG VITE_API_URL=http://localhost:8080/api
ENV VITE_API_URL=$VITE_API_URL
ARG MF_INVENTARIO_URL=http://localhost:5101/
ENV MF_INVENTARIO_URL=$MF_INVENTARIO_URL
ARG MF_VENCIMIENTOS_URL=http://localhost:5102/
ENV MF_VENCIMIENTOS_URL=$MF_VENCIMIENTOS_URL
ARG MF_PLANIFICACION_DE_DEMANDA_URL=http://localhost:5103/
ENV MF_PLANIFICACION_DE_DEMANDA_URL=$MF_PLANIFICACION_DE_DEMANDA_URL
ARG MF_ABASTECIMIENTO_URL=http://localhost:5104/
ENV MF_ABASTECIMIENTO_URL=$MF_ABASTECIMIENTO_URL
ARG MF_SEGURIDAD_Y_AUDITORIA_URL=http://localhost:5105/
ENV MF_SEGURIDAD_Y_AUDITORIA_URL=$MF_SEGURIDAD_Y_AUDITORIA_URL
ARG MF_INTEGRACIONES_URL=http://localhost:5106/
ENV MF_INTEGRACIONES_URL=$MF_INTEGRACIONES_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
