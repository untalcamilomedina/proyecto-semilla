# Dockerfile para frontend Next.js - Proyecto Semilla
FROM node:18-alpine

# Instalar dependencias del sistema
RUN apk add --no-cache libc6-compat curl

# Crear usuario no privilegiado
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Establecer directorio de trabajo
WORKDIR /app

# Argumentos para variables de entorno
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_API_TIMEOUT
ARG NEXT_PUBLIC_APP_NAME
ARG NEXT_PUBLIC_APP_VERSION
ARG NEXT_PUBLIC_ENVIRONMENT
ARG NEXT_PUBLIC_ENABLE_DEVTOOLS
ARG NEXT_PUBLIC_LOG_LEVEL
ARG NEXT_PUBLIC_ENABLE_COLLABORATION
ARG NEXT_PUBLIC_ENABLE_MARKETPLACE
ARG NEXT_PUBLIC_ENABLE_ANALYTICS
ARG NEXT_PUBLIC_DEMO_EMAIL
ARG NEXT_PUBLIC_DEMO_PASSWORD
ARG NEXT_PUBLIC_DEFAULT_TENANT_ID

# Establecer variables de entorno para el build
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_TIMEOUT=$NEXT_PUBLIC_API_TIMEOUT
ENV NEXT_PUBLIC_APP_NAME=$NEXT_PUBLIC_APP_NAME
ENV NEXT_PUBLIC_APP_VERSION=$NEXT_PUBLIC_APP_VERSION
ENV NEXT_PUBLIC_ENVIRONMENT=$NEXT_PUBLIC_ENVIRONMENT
ENV NEXT_PUBLIC_ENABLE_DEVTOOLS=$NEXT_PUBLIC_ENABLE_DEVTOOLS
ENV NEXT_PUBLIC_LOG_LEVEL=$NEXT_PUBLIC_LOG_LEVEL
ENV NEXT_PUBLIC_ENABLE_COLLABORATION=$NEXT_PUBLIC_ENABLE_COLLABORATION
ENV NEXT_PUBLIC_ENABLE_MARKETPLACE=$NEXT_PUBLIC_ENABLE_MARKETPLACE
ENV NEXT_PUBLIC_ENABLE_ANALYTICS=$NEXT_PUBLIC_ENABLE_ANALYTICS
ENV NEXT_PUBLIC_DEMO_EMAIL=$NEXT_PUBLIC_DEMO_EMAIL
ENV NEXT_PUBLIC_DEMO_PASSWORD=$NEXT_PUBLIC_DEMO_PASSWORD
ENV NEXT_PUBLIC_DEFAULT_TENANT_ID=$NEXT_PUBLIC_DEFAULT_TENANT_ID

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
    CMD curl -f http://localhost:3000/ || exit 1

# Comando para ejecutar la aplicación
CMD ["npm", "run", "start"]