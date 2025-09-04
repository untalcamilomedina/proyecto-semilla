# Dockerfile para backend FastAPI - Proyecto Semilla
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado
RUN useradd --create-home --shell /bin/bash app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias de Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY backend/ .

# Cambiar propietario de los archivos
RUN chown -R app:app /app

# Cambiar a usuario no privilegiado
USER app

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]