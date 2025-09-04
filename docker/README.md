# 🐳 Docker - Proyecto Semilla

Este directorio contiene configuraciones Docker para diferentes entornos de despliegue.

## 🏗️ Estructura (Planeada)

```
docker/
├── README.md                   # Este archivo
├── docker-compose.yml         # Configuración principal de desarrollo
├── docker-compose.prod.yml    # Override para producción
├── docker-compose.test.yml    # Override para testing
├── .env.example               # Variables de entorno ejemplo
├── backend/
│   ├── Dockerfile             # Imagen de backend (FastAPI)
│   ├── Dockerfile.prod        # Imagen optimizada para producción
│   └── requirements.txt       # Dependencias Python
├── frontend/
│   ├── Dockerfile             # Imagen de frontend (Next.js)
│   ├── Dockerfile.prod        # Imagen optimizada para producción
│   └── nginx.conf            # Configuración Nginx para producción
├── database/
│   ├── init/                 # Scripts de inicialización
│   │   ├── 01-init-db.sql    # Crear base de datos
│   │   ├── 02-enable-rls.sql # Habilitar Row-Level Security
│   │   └── 03-extensions.sql # Extensiones PostgreSQL
│   └── backups/              # Directorio para backups
├── nginx/
│   ├── nginx.conf            # Configuración proxy reverso
│   ├── ssl/                  # Certificados SSL
│   └── templates/            # Templates de configuración
├── monitoring/               # Monitoreo (futuro)
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── alerts/
└── scripts/                  # Scripts de utilidades Docker
    ├── build-all.sh          # Build todas las imágenes
    ├── clean-up.sh           # Limpiar imágenes y contenedores
    └── health-check.sh       # Verificar salud de servicios
```

## 🚀 Servicios Principales

### 🗄️ Base de Datos (PostgreSQL)
```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: proyecto_semilla
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
```

**Características**:
- PostgreSQL 15 con Alpine Linux (imagen ligera)
- Scripts de inicialización automática
- Volumen persistente para datos
- Row-Level Security habilitado por defecto

### ⚡ Cache (Redis)
```yaml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
```

**Características**:
- Redis 7 para cache y sesiones
- Persistencia habilitada
- Configuración optimizada para desarrollo

### 🐍 Backend (FastAPI)
```yaml
services:
  backend:
    build:
      context: ../backend
      dockerfile: ../docker/backend/Dockerfile
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@db:5432/proyecto_semilla
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ../backend:/app
```

**Características**:
- Hot reload para desarrollo
- Variables de entorno configurables
- Dependencias automáticas
- Volumen montado para desarrollo

### ⚛️ Frontend (Next.js)
```yaml
services:
  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/frontend/Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
    ports:
      - "3000:3000"
    volumes:
      - ../frontend:/app
      - /app/node_modules
```

**Características**:
- Next.js con hot reload
- Variables de entorno para desarrollo
- Node modules optimizados
- Puerto 3000 expuesto

### 🔀 Nginx (Proxy Reverso)
```yaml
services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
```

**Características**:
- Proxy reverso para frontend y backend
- Configuración SSL ready
- Load balancing (para futuro scaling)
- Compresión gzip habilitada

## 🔧 Comandos Docker

### 💻 Desarrollo Local
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Levantar servicio específico
docker-compose up -d db redis

# Rebuild servicios tras cambios
docker-compose up -d --build

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v
```

### 🏭 Producción
```bash
# Usar configuración de producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Build imágenes optimizadas
docker-compose -f docker-compose.prod.yml build --no-cache

# Ver estado de servicios
docker-compose ps

# Escalar servicios
docker-compose up -d --scale backend=3
```

### 🧪 Testing
```bash
# Ejecutar tests en contenedores
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Tests específicos
docker-compose exec backend pytest
docker-compose exec frontend npm test
```

## 📋 Variables de Entorno

### 🔧 Archivo `.env`
```env
# Base de datos
DB_PASSWORD=super_secure_password_here
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla

# Backend
JWT_SECRET=your_jwt_secret_key_here
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Email (futuro)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Almacenamiento (futuro)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=proyecto-semilla-uploads
```

### 🔒 Secretos de Producción
```bash
# Usando Docker Secrets (Docker Swarm)
echo "super_secure_password" | docker secret create db_password -
echo "jwt_secret_key_here" | docker secret create jwt_secret -

# Usando variables de entorno del sistema
export DB_PASSWORD=$(cat /run/secrets/db_password)
export JWT_SECRET=$(cat /run/secrets/jwt_secret)
```

## 🏗️ Dockerfiles Optimizados

### Backend Dockerfile
```dockerfile
# docker/backend/Dockerfile
FROM python:3.11-slim as base

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Usuario no privilegiado
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Imagen de producción
FROM base as production
USER root
RUN pip install gunicorn
USER app
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Frontend Dockerfile
```dockerfile
# docker/frontend/Dockerfile
FROM node:18-alpine as base

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copiar código fuente
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# Imagen de producción
FROM base as builder
RUN npm run build

FROM node:18-alpine as production
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production && npm cache clean --force

EXPOSE 3000
CMD ["npm", "start"]
```

## 🔍 Monitoreo y Logging

### 📊 Health Checks
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d proyecto_semilla"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 📝 Logging Centralizado
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        
  # Con ELK Stack (futuro)
  elasticsearch:
    image: elasticsearch:8.8.0
    
  logstash:
    image: logstash:8.8.0
    
  kibana:
    image: kibana:8.8.0
```

## 🛡️ Seguridad

### 🔒 Best Practices
- **No privileged containers**: Todos los contenedores corren como usuarios no privilegiados
- **Secrets management**: Uso de Docker Secrets o variables de entorno
- **Network isolation**: Redes Docker separadas por función
- **Image scanning**: Análisis de vulnerabilidades en imágenes
- **Resource limits**: Límites de memoria y CPU

### 🌐 Configuración Nginx Segura
```nginx
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚀 Estado de Desarrollo

### ✅ Fase 1 (v0.1.0-v0.3.0)
- [ ] docker-compose.yml básico para desarrollo
- [ ] Dockerfiles para backend y frontend
- [ ] Configuración PostgreSQL con RLS
- [ ] Scripts de inicialización de BD
- [ ] Health checks básicos

### 🔮 Fases Futuras
- [ ] Configuración optimizada para producción
- [ ] Nginx como proxy reverso
- [ ] SSL/TLS automatizado con Let's Encrypt
- [ ] Monitoreo con Prometheus + Grafana
- [ ] Logging centralizado con ELK Stack
- [ ] Auto-scaling con Docker Swarm/Kubernetes

---

*Las configuraciones Docker serán implementadas progresivamente, priorizando un entorno de desarrollo funcional en la Fase 1.*