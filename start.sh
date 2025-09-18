#!/bin/bash

# 🌱 Proyecto Semilla - Inicio Simple
# Inspirado en WordPress - 3 pasos simples

echo "🌱 PROYECTO SEMILLA"
echo "==================="
echo ""
echo "🚀 PASO 1: Levantando servicios..."
echo ""

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    echo "   Por favor inicia Docker Desktop y vuelve a ejecutar este script"
    exit 1
fi

# Crear .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando configuración básica..."
    cat > .env << 'EOF'
# Configuración automática de Proyecto Semilla
DB_PASSWORD=changeme123
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla
JWT_SECRET=super_secret_jwt_key_for_development_only_change_in_production
CORS_ORIGINS=http://localhost:7701,http://localhost:7777
DEBUG=true
NEXT_PUBLIC_API_URL=http://localhost:7777
LOG_LEVEL=INFO
EOF
fi

# Crear .env.local para frontend si no existe
if [ ! -f frontend/.env.local ]; then
    cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:7777
NEXT_PUBLIC_DEMO_EMAIL=admin@example.com
NEXT_PUBLIC_DEMO_PASSWORD=admin123
EOF
fi

# Levantar todos los servicios
echo "🐳 Iniciando servicios Docker..."
docker-compose up -d

echo ""
echo "⏳ Preparando servicios..."
sleep 10

echo ""
echo "🎉 ¡PLATAFORMA LISTA!"
echo "===================="
echo ""
echo "🌐 PASO 2: Abre tu navegador"
echo "   👉 http://localhost:7701"
echo ""
echo "⚙️  PASO 3: Configuración inicial"
echo "   📋 Si es primera vez, verás el wizard de configuración"
echo "   👤 Crea tu cuenta de superadministrador"
echo "   🚀 ¡Tu plataforma enterprise estará lista!"
echo ""
echo "💡 Información importante:"
echo "   - Usuario: El email que configures"
echo "   - Contraseña: La que configures"
echo "   - Tendrás acceso completo como superadmin"
echo ""
echo "🔧 Troubleshooting:"
echo "   docker-compose logs        # Ver logs"
echo "   docker-compose restart     # Reiniciar servicios"
echo "   docker-compose down        # Detener todo"
echo ""
echo "🎊 ¡Bienvenido al futuro del desarrollo Vibecoding!"
echo "   Tu plataforma SaaS enterprise-native está lista 🚀"