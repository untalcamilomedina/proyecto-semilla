# 🚀 Guía de Instalación - Proyecto Semilla

## Requisitos Previos

- **Docker** y **Docker Compose** instalados
- **Python 3.11+** (opcional, solo para desarrollo local)
- **Git** para clonar el repositorio

## Instalación Simple (Recomendado)

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/proyecto-semilla/proyecto-semilla.git
cd proyecto-semilla
```

### Paso 2: Ejecutar setup automático
```bash
./scripts/setup.sh
```

El script setup:
- ✅ Verifica que Docker esté corriendo
- ✅ Crea archivos de configuración (.env)
- ✅ Levanta servicios básicos (PostgreSQL + Redis)
- ✅ Ejecuta migraciones de base de datos
- ✅ Muestra instrucciones para próximos pasos

### Paso 3: Levantar servicios completos
```bash
docker-compose up -d backend frontend
```

### Paso 4: Acceder al sistema
- **Frontend**: http://localhost:7701
- **Si es primera vez**: Verás el wizard de configuración inicial
- **Después de configurar**: Podrás iniciar sesión normalmente

### Paso 4: Acceder a la aplicación
- **Frontend**: http://localhost:7701
- **Backend API**: http://localhost:7777
- **Documentación API**: http://localhost:7777/docs
- **MCP Server**: http://localhost:8001/docs

## Credenciales de Acceso

Después de la instalación, puedes acceder con:
- **Usuario**: admin@example.com
- **Contraseña**: admin123

## Instalación Manual (Alternativa)

Si prefieres configurar manualmente:

### 1. Configurar entorno
```bash
cp .env.example .env
# Edita .env con tus configuraciones
```

### 2. Configurar frontend
```bash
cp frontend/.env.local.example frontend/.env.local
# Edita frontend/.env.local si es necesario
```

### 3. Iniciar servicios
```bash
docker-compose up -d
```

### 4. Ejecutar migraciones
```bash
docker-compose exec backend alembic upgrade head
```

### 5. Crear datos iniciales
```bash
docker-compose exec backend python app/initial_data.py
```

## Solución de Problemas

### Error: "Not authenticated"
- Verifica que los servicios estén ejecutándose: `docker-compose ps`
- Revisa los logs: `docker-compose logs backend`
- Verifica la configuración en `.env`

### Error: "Connection refused"
- Asegúrate de que Docker esté ejecutándose
- Espera a que los servicios estén healthy: `docker-compose ps`

### Error: "Port already in use"
- Los puertos están configurados para evitar conflictos:
  - PostgreSQL: 5433 (interno 5432)
  - Redis: 6380 (interno 6379)
  - Frontend: 7701 (interno 3000)
  - Backend: 7777 (interno 8000)
  - MCP Server: 8001

### Verificar estado de servicios
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs backend

# Ver logs de todos los servicios
docker-compose logs
```

## Configuración de Desarrollo

Para desarrollo local sin Docker:

### Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.initial_data
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Variables de Entorno

### Archivo .env principal
```env
# Base de datos
DB_PASSWORD=changeme123
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla

# Backend
JWT_SECRET=your_jwt_secret_key_at_least_64_characters_long_for_security
CORS_ORIGINS=http://localhost:7701,http://localhost:7777
DEBUG=true

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:7777
```

### Archivo frontend/.env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:7777
NEXT_PUBLIC_DEMO_EMAIL=admin@example.com
NEXT_PUBLIC_DEMO_PASSWORD=admin123
NEXT_PUBLIC_DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000001
```

## Siguientes Pasos

Después de la instalación exitosa:

1. **Explora la aplicación** en http://localhost:7701
2. **Revisa la documentación API** en http://localhost:7777/docs
3. **Configura usuarios adicionales** desde el panel de administración
4. **Personaliza la configuración** según tus necesidades

## Soporte

Si encuentras problemas:
1. Revisa los logs de Docker
2. Verifica la configuración de puertos
3. Asegúrate de que Docker tenga suficientes recursos
4. Consulta la documentación en `docs/`