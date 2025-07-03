################ Stage 1 – Build ################
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration=production     
# → dist/frontend/

################ Stage 2 – Nginx #################
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

COPY --from=builder /app/dist/frontend/browser/ .

RUN rm -f /usr/share/nginx/html/index.nginx-debian.html 2>/dev/null || true

ARG API_URL=http://backend:8000
RUN sed -i "s|{{API_URL}}|${API_URL}|g" index.html || true

EXPOSE 80
