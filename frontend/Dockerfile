FROM node:20-alpine AS builder    
WORKDIR /app

COPY package*.json ./
RUN npm ci                    

COPY . .
RUN npm run build -- --configuration=production
# Il build finisce in /app/dist/<nome-app>

##########################
# Stage 2: image NGINX   #
##########################
FROM nginx:stable-alpine          
WORKDIR /usr/share/nginx/html
COPY --from=builder /app/dist/frontend/* . 

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
