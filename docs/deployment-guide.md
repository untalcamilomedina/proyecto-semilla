# 🚀 Deployment Guide - Proyecto Semilla
## Guía Completa de Deployment para Producción

**Versión:** 0.5.0
**Última actualización:** 5 de septiembre de 2025

---

## 📋 Tabla de Contenidos

- [Prerrequisitos](#-prerrequisitos)
- [Configuración del Entorno](#-configuración-del-entorno)
- [Deployment con Docker](#-deployment-con-docker)
- [Configuración de Producción](#-configuración-de-producción)
- [Monitoreo y Alertas](#-monitoreo-y-alertas)
- [Backup y Recovery](#-backup-y-recovery)
- [Escalado](#-escalado)
- [Troubleshooting](#-troubleshooting)

---

## 🛠️ Prerrequisitos

### **Requisitos del Sistema**
- **Servidor:** Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **CPU:** 2 cores mínimo, 4 cores recomendado
- **RAM:** 4GB mínimo, 8GB recomendado
- **Disco:** 20GB SSD mínimo
- **Red:** 100Mbps conexión estable

### **Software Requerido**
```bash
# Docker y Docker Compose
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Git
sudo apt install git

# Certbot (para SSL)
sudo apt install certbot python3-certbot-nginx

# Monitoring tools
sudo apt install prometheus node-exporter
```

### **Puertos Requeridos**
| Servicio | Puerto | Protocolo | Descripción |
|----------|--------|-----------|-------------|
| Nginx | 80, 443 | HTTP/HTTPS | Reverse proxy y SSL |
| PostgreSQL | 5432 | TCP | Base de datos |
| Redis | 6379 | TCP | Cache y sesiones |
| Backend API | 8000 | HTTP | API FastAPI |
| Frontend | 3000 | HTTP | Next.js app |
| Prometheus | 9090 | HTTP | Monitoring |
| Grafana | 3001 | HTTP | Dashboards |

---

## ⚙️ Configuración del Entorno

### **1. Clonar el Repositorio**
```bash
# Crear directorio de la aplicación
sudo mkdir -p /opt/proyecto-semilla
cd /opt/proyecto-semilla

# Clonar repositorio
git clone https://github.com/proyecto-semilla/proyecto-semilla.git .
git checkout main  # O la versión específica que desees deployar
```

### **2. Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env.production

# Editar variables de producción
nano .env.production
```

**Contenido del archivo `.env.production`:**
```bash
# Base de datos
DATABASE_URL=postgresql://proyecto_semilla_prod:secure_password_123@localhost:5432/proyecto_semilla_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# JWT
SECRET_KEY=your-super-secure-jwt-secret-key-here-32-chars-minimum
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_ENABLED=true

# Security
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### **3. Configurar Usuario del Sistema**
```bash
# Crear usuario para la aplicación
sudo useradd -r -s /bin/false proyecto_semilla

# Cambiar propietario de los archivos
sudo chown -R proyecto_semilla:proyecto_semilla /opt/proyecto-semilla

# Cambiar permisos
sudo chmod 755 /opt/proyecto-semilla
sudo chmod 600 /opt/proyecto-semilla/.env.production
```

---

## 🐳 Deployment con Docker

### **1. Configurar Docker Compose para Producción**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Base de datos PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: proyecto_semilla_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: proyecto_semilla_prod
      POSTGRES_USER: proyecto_semilla_prod
      POSTGRES_PASSWORD: secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/database/init:/docker-entrypoint-initdb.d
    networks:
      - proyecto_semilla_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U proyecto_semilla_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: proyecto_semilla_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - proyecto_semilla_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API
  backend:
    image: proyecto-semilla-backend:latest
    container_name: proyecto_semilla_backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - proyecto_semilla_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    image: proyecto-semilla-frontend:latest
    container_name: proyecto_semilla_frontend
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    networks:
      - proyecto_semilla_network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: proyecto_semilla_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - proyecto_semilla_network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: proyecto_semilla_prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - proyecto_semilla_network

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: proyecto_semilla_grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_grafana_password
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - proyecto_semilla_network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  proyecto_semilla_network:
    driver: bridge
```

### **2. Construir Imágenes de Producción**
```bash
# Construir imágenes con multi-stage builds
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Verificar imágenes construidas
docker images | grep proyecto-semilla
```

### **3. Ejecutar Migraciones de Base de Datos**
```bash
# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Verificar estado de migraciones
docker-compose -f docker-compose.prod.yml run --rm backend alembic current
```

### **4. Iniciar Servicios**
```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.prod.yml up -d

# Verificar estado de servicios
docker-compose -f docker-compose.prod.yml ps

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔒 Configuración de Producción

### **1. Configurar SSL con Let's Encrypt**
```bash
# Detener nginx temporalmente
docker-compose -f docker-compose.prod.yml stop nginx

# Ejecutar certbot
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copiar certificados al contenedor
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/

# Reiniciar nginx
docker-compose -f docker-compose.prod.yml start nginx
```

### **2. Configurar Nginx**
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # API endpoints
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Rate limiting for API
            limit_req zone=api burst=20 nodelay;

            # CORS
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Tenant-ID";
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### **3. Configurar Firewall**
```bash
# Configurar UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 9090  # Prometheus
sudo ufw allow 3001  # Grafana

# Verificar reglas
sudo ufw status
```

---

## 📊 Monitoreo y Alertas

### **1. Configurar Prometheus**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'proyecto-semilla-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'proyecto-semilla-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### **2. Configurar Alertas**
```yaml
# monitoring/alert_rules.yml
groups:
  - name: proyecto_semilla_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}%"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"
          description: "PostgreSQL has been down for more than 1 minute"

      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"
```

### **3. Configurar Grafana**
```bash
# Acceder a Grafana
open http://your-server:3001

# Credenciales por defecto
Username: admin
Password: secure_grafana_password

# Importar dashboards
# Dashboard ID: 1860 (Node Exporter)
# Dashboard ID: 9628 (PostgreSQL)
# Dashboard ID: 11835 (Redis)
```

---

## 💾 Backup y Recovery

### **1. Configurar Backups Automáticos**
```bash
# Crear script de backup
cat > /opt/proyecto-semilla/scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups/proyecto-semilla"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U proyecto_semilla_prod proyecto_semilla_prod > $BACKUP_DIR/db_$DATE.sql

# Backup de Redis
docker-compose -f docker-compose.prod.yml exec -T redis redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup de archivos estáticos
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/proyecto-semilla/uploads/

# Comprimir backup
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR db_$DATE.sql redis_$DATE.rdb uploads_$DATE.tar.gz

# Limpiar archivos temporales
rm $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/redis_$DATE.rdb $BACKUP_DIR/uploads_$DATE.tar.gz

# Limpiar backups antiguos
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.tar.gz"
EOF

# Hacer ejecutable
chmod +x /opt/proyecto-semilla/scripts/backup.sh
```

### **2. Configurar Cron para Backups**
```bash
# Editar crontab
sudo crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * /opt/proyecto-semilla/scripts/backup.sh

# Verificar crontab
sudo crontab -l
```

### **3. Proceso de Recovery**
```bash
# Detener servicios
docker-compose -f docker-compose.prod.yml down

# Restaurar base de datos
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec -T db psql -U proyecto_semilla_prod proyecto_semilla_prod < /opt/backups/proyecto-semilla/db_20230905_020000.sql

# Restaurar Redis
docker-compose -f docker-compose.prod.yml exec -T redis redis-cli --rdb /data/dump.rdb < /opt/backups/proyecto-semilla/redis_20230905_020000.rdb

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Verificar restauración
curl -f https://yourdomain.com/health
```

---

## 📈 Escalado

### **1. Escalado Horizontal**
```bash
# Escalar backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Escalar frontend
docker-compose -f docker-compose.prod.yml up -d --scale frontend=2

# Configurar load balancer
upstream backend {
    server backend:8000;
    server backend:8001;
    server backend:8002;
}

upstream frontend {
    server frontend:3000;
    server frontend:3001;
}
```

### **2. Configurar Redis Cluster**
```yaml
# docker-compose.redis-cluster.yml
version: '3.8'

services:
  redis-1:
    image: redis:7-alpine
    command: redis-server /etc/redis/redis.conf
    volumes:
      - ./redis/cluster.conf:/etc/redis/redis.conf
    networks:
      - redis-cluster

  redis-2:
    image: redis:7-alpine
    command: redis-server /etc/redis/redis.conf
    volumes:
      - ./redis/cluster.conf:/etc/redis/redis.conf
    networks:
      - redis-cluster

  redis-3:
    image: redis:7-alpine
    command: redis-server /etc/redis/redis.conf
    volumes:
      - ./redis/cluster.conf:/etc/redis/redis.conf
    networks:
      - redis-cluster
```

### **3. Database Read Replicas**
```yaml
# Configurar PostgreSQL streaming replication
# postgresql.conf en master
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64

# recovery.conf en replica
primary_conninfo = 'host=master_ip port=5432 user=replication_user password=replication_password'
```

---

## 🔧 Troubleshooting

### **Problemas Comunes en Producción**

#### **Servicio No Inicia**
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs <service_name>

# Verificar health checks
docker-compose -f docker-compose.prod.yml ps

# Reiniciar servicio específico
docker-compose -f docker-compose.prod.yml restart <service_name>
```

#### **Alta Latencia**
```bash
# Verificar métricas de Prometheus
curl http://localhost:9090/api/v1/query?query=http_request_duration_seconds

# Verificar uso de recursos
docker stats

# Verificar conexiones de base de datos
docker-compose -f docker-compose.prod.yml exec db psql -U proyecto_semilla_prod -c "SELECT count(*) FROM pg_stat_activity;"
```

#### **Out of Memory**
```bash
# Verificar límites de memoria
docker-compose -f docker-compose.prod.yml exec backend cat /proc/meminfo

# Ajustar límites en docker-compose
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

### **Comandos Útiles para Debugging**
```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f backend

# Ejecutar comandos en contenedor
docker-compose -f docker-compose.prod.yml exec backend bash

# Ver métricas de sistema
docker stats

# Ver uso de red
docker network ls
docker network inspect proyecto_semilla_network

# Backup manual
/opt/proyecto-semilla/scripts/backup.sh

# Health check manual
curl -f https://yourdomain.com/health
```

---

## 📞 Soporte y Mantenimiento

### **Actualizaciones**
```bash
# Actualizar aplicación
git pull origin main
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Verificar actualización
curl -f https://yourdomain.com/health
```

### **Monitoreo Continuo**
- **Uptime:** 99.9% SLA
- **Response Time:** <100ms P95
- **Error Rate:** <0.1%
- **CPU Usage:** <70%
- **Memory Usage:** <80%

### **Contactos de Emergencia**
- **Soporte Técnico:** support@proyecto-semilla.dev
- **Alertas Críticas:** +57 300 123 4567
- **Documentación:** [docs.proyecto-semilla.dev](https://docs.proyecto-semilla.dev)

---

*"Esta guía de deployment se mantiene actualizada con las mejores prácticas de producción. Última actualización: 5 de septiembre de 2025"*

🇨🇴 **Proyecto Semilla** - Production Deployment Guide v0.5.0