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
RUN npm ci # Install all dependencies, including devDependencies

# Copiar código fuente, excluyendo archivos de desarrollo
COPY frontend/ .
# Remove .env.local to prevent it from interfering with production builds
RUN rm -f .env.local

# Explicitly install shadcn/ui dependencies
RUN npm install class-variance-authority clsx tailwind-merge lucide-react

# Build the Next.js application
RUN npm run build

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
CMD ["npm", "run", "start"]