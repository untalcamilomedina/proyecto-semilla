# Dockerfile para frontend Next.js - Proyecto Semilla
FROM node:18-alpine

# Instalar dependencias del sistema
RUN apk add --no-cache libc6-compat curl

# Crear usuario no privilegiado
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json e instalar dependencias
COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copiar código fuente
COPY frontend/ .

# Cambiar propietario de los archivos
RUN chown -R nextjs:nodejs /app

# Cambiar a usuario no privilegiado
USER nextjs

# Exponer puerto
EXPOSE 3000

# Variables de entorno
ENV PORT=3000
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Comando para ejecutar la aplicación
CMD ["npm", "run", "dev"]