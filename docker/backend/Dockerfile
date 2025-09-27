# Multi-stage Dockerfile para backend FastAPI - Proyecto Semilla

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Instalar dependencias del sistema para build
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado
RUN useradd --create-home --shell /bin/bash app

# Establecer directorio de trabajo
WORKDIR /app

# Instalar Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

# Instalar solo runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado
RUN useradd --create-home --shell /bin/bash app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar Python packages desde builder stage
COPY --from=builder /root/.local /home/app/.local
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Asegurar que el PATH incluya los paquetes instalados
ENV PATH=/home/app/.local/bin:$PATH

# Copiar código de la aplicación
COPY backend/ .

# Cambiar propietario de los archivos
RUN chown -R app:app /app /home/app/.local

# Cambiar a usuario no privilegiado
USER app

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]