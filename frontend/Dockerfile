# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copiamos los archivos de dependencias
COPY package.json package-lock.json* ./

# Instalamos las dependencias
RUN npm install

# Copiamos el resto del código de Next.js
COPY . .

# Construimos la aplicación de producción
RUN npm run build

EXPOSE 3000

# Arrancamos Next.js
CMD ["npm", "run", "start"]