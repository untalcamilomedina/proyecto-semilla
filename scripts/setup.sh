#!/bin/bash

# Proyecto Semilla - Setup Simple
# Script para configurar el entorno básico

echo "🌱 PROYECTO SEMILLA - SETUP SIMPLE"
echo "=================================="

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

echo "✅ Docker está corriendo"

# Crear archivo .env básico si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
# Proyecto Semilla - Configuración de Entorno
# Generado automáticamente por setup.sh

# Base de datos
DB_PASSWORD=changeme123
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla

# Backend
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=http://localhost:7701,http://localhost:7777
DEBUG=true

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:7777

# Configuración adicional
LOG_LEVEL=INFO
EOF
    echo "✅ Archivo .env creado"
else
    echo "ℹ️  Archivo .env ya existe"
fi

# Crear archivo .env para frontend si no existe
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creando archivo frontend/.env.local..."
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:7777
NEXT_PUBLIC_DEMO_EMAIL=admin@example.com
NEXT_PUBLIC_DEMO_PASSWORD=admin123
NEXT_PUBLIC_DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000001
EOF
    echo "✅ Archivo frontend/.env.local creado"
else
    echo "ℹ️  Archivo frontend/.env.local ya existe"
fi

echo ""
echo "🚀 Levantando servicios Docker..."
docker-compose up -d db redis

echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

echo "📦 Ejecutando migraciones de base de datos..."
docker-compose exec -T backend sh -c "PYTHONPATH=/app alembic upgrade head"

echo ""
echo "🎉 ¡Setup completado!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Levantar el backend y frontend:"
echo "   docker-compose up -d backend frontend"
echo ""
echo "2. Acceder al frontend:"
echo "   http://localhost:7701"
echo ""
echo "3. Si es la primera vez, verás el formulario de configuración inicial"
echo "   Crea tu cuenta de superadministrador"
echo ""
echo "4. Una vez configurado, podrás iniciar sesión con tus credenciales"
echo ""
echo "🔐 Credenciales por defecto (después de configuración):"
echo "   - Usuario: admin@example.com"
echo "   - Contraseña: admin123"