# 📦 GUÍA DE DESPLIEGUE EN PRODUCCIÓN

**Proyecto Semilla** - Deployment Guide
**Versión:** 1.0.0
**Última Actualización:** Noviembre 2025

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del Servidor](#preparación-del-servidor)
3. [Configuración de Seguridad](#configuración-de-seguridad)
4. [Instalación](#instalación)
5. [Configuración de HTTPS/SSL](#configuración-de-httpsssl)
6. [Despliegue](#despliegue)
7. [Verificación Post-Despliegue](#verificación-post-despliegue)
8. [Mantenimiento](#mantenimiento)
9. [Troubleshooting](#troubleshooting)

---

## 1. Requisitos Previos

### Hardware Mínimo

| Recurso | Desarrollo | Producción (Pequeña) | Producción (Grande) |
|---------|------------|---------------------|---------------------|
| CPU | 2 cores | 4 cores | 8+ cores |
| RAM | 4 GB | 8 GB | 16+ GB |
| Disco | 20 GB | 50 GB | 100+ GB SSD |
| Network | 100 Mbps | 1 Gbps | 10 Gbps |

### Software

- **Sistema Operativo:** Ubuntu 22.04 LTS (recomendado) o CentOS/RHEL 8+
- **Docker:** 24.0+
- **Docker Compose:** 2.20+
- **Git:** 2.30+
- **Nginx:** 1.24+ (opcional si usas reverse proxy externo)
- **OpenSSL:** 3.0+ (para generar secrets)

### Servicios Externos (Opcionales)

- **Servicio de Email:** Para notificaciones (SMTP)
- **Servicio de Backup:** S3, GCS, o similar
- **Monitoreo:** Prometheus, Grafana, o similar
- **Logs:** ELK Stack o Loki

---

## 2. Preparación del Servidor

### 2.1 Actualizar Sistema

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2.2 Instalar Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 2.3 Configurar Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 2.4 Crear Usuario de Aplicación

```bash
sudo useradd -m -s /bin/bash proyecto_semilla
sudo usermod -aG docker proyecto_semilla
sudo su - proyecto_semilla
```

---

## 3. Configuración de Seguridad

### 3.1 Generar Credenciales de Producción

```bash
cd /home/proyecto_semilla
git clone https://github.com/your-org/proyecto-semilla.git
cd proyecto-semilla

# Ejecutar script de setup de producción
./scripts/setup_production.sh
```

El script generará automáticamente:
- ✅ JWT_SECRET (64 caracteres)
- ✅ DB_PASSWORD (32 caracteres)
- ✅ Archivo `.env.production` completo

### 3.2 Personalizar Configuración

Edita `.env.production` y actualiza:

```bash
# Dominio de producción
COOKIE_DOMAIN=tu-dominio.com
BACKEND_CORS_ORIGINS='["https://tu-dominio.com","https://www.tu-dominio.com"]'

# Email del administrador (para SSL)
ADMIN_EMAIL=admin@tu-dominio.com

# (Opcional) Configurar SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@tu-dominio.com
SMTP_PASSWORD=tu_contraseña_smtp
```

### 3.3 Proteger Archivos Sensibles

```bash
# Permisos restrictivos para archivos de configuración
chmod 600 .env.production
chmod 600 frontend/.env.production.local

# Verificar .gitignore
echo ".env.production" >> .gitignore
echo "frontend/.env.production.local" >> .gitignore
```

---

## 4. Instalación

### 4.1 Clonar Repositorio (si aún no lo hiciste)

```bash
cd /home/proyecto_semilla
git clone https://github.com/your-org/proyecto-semilla.git
cd proyecto-semilla
```

### 4.2 Configurar Variables de Entorno

```bash
# Usar el archivo generado por setup_production.sh
cp .env.production .env

# O si ya tienes un .env, verifica que tenga todos los valores necesarios
./scripts/verify_production_readiness.sh
```

### 4.3 Preparar Docker

```bash
# Descargar imágenes base (opcional, para acelerar primer deploy)
docker-compose -f docker-compose.prod.yml pull
```

---

## 5. Configuración de HTTPS/SSL

### Opción A: Let's Encrypt (Recomendado)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Generar certificados
sudo certbot certonly --standalone \
  -d tu-dominio.com \
  -d www.tu-dominio.com \
  --email admin@tu-dominio.com \
  --agree-tos \
  --non-interactive

# Copiar certificados a proyecto
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem docker/nginx/ssl/
sudo chown -R proyecto_semilla:proyecto_semilla docker/nginx/ssl
```

### Opción B: Certificado Personalizado

```bash
# Si tienes certificados propios
mkdir -p docker/nginx/ssl
cp tu_certificado.pem docker/nginx/ssl/fullchain.pem
cp tu_llave_privada.pem docker/nginx/ssl/privkey.pem
chmod 600 docker/nginx/ssl/*.pem
```

### 5.1 Configurar Nginx

Crea o edita `docker/nginx/nginx.prod.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API Backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health Check
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
```

---

## 6. Despliegue

### 6.1 Primera Vez - Construcción e Inicio

```bash
# Construir imágenes de producción
docker-compose -f docker-compose.prod.yml build --no-cache

# Levantar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f
```

### 6.2 Verificar Servicios

```bash
# Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Todos deberían estar "Up" y "healthy"
```

### 6.3 Acceder al Wizard de Instalación

1. Abre tu navegador en `https://tu-dominio.com`
2. Verás el wizard de instalación en 3 pasos
3. **Paso 1:** Verificación automática de requisitos
4. **Paso 2:** Crea tu usuario superadministrador
5. **Paso 3:** Completado - Accede al dashboard

---

## 7. Verificación Post-Despliegue

### 7.1 Script de Verificación

```bash
# Ejecutar verificación completa
./scripts/verify_production_readiness.sh
```

### 7.2 Checklist Manual

```bash
# ✅ Servicios corriendo
docker ps | grep proyecto_semilla

# ✅ Backend saludable
curl -k https://tu-dominio.com/api/v1/health

# ✅ Frontend accesible
curl -k https://tu-dominio.com

# ✅ Base de datos conectada
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "from app.core.database import engine; engine.connect()"

# ✅ Redis funcionando
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# ✅ Logs sin errores críticos
docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i error
```

### 7.3 Pruebas Funcionales

- [ ] Registro de usuario funciona
- [ ] Login funciona
- [ ] Creación de tenant funciona
- [ ] CRUD de usuarios funciona
- [ ] CRUD de roles funciona
- [ ] Permisos se aplican correctamente
- [ ] WebSockets funcionan (si aplica)

---

## 8. Mantenimiento

### 8.1 Backups Automáticos

```bash
# Crear backup manual
./scripts/backup_database.sh

# Configurar backup automático (cron)
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * cd /home/proyecto_semilla/proyecto-semilla && ./scripts/backup_database.sh >> /var/log/proyecto_semilla_backup.log 2>&1
```

### 8.2 Actualización del Sistema

```bash
# 1. Crear backup antes de actualizar
./scripts/backup_database.sh

# 2. Detener servicios
docker-compose -f docker-compose.prod.yml down

# 3. Actualizar código
git pull origin main

# 4. Reconstruir imágenes
docker-compose -f docker-compose.prod.yml build

# 5. Ejecutar migraciones
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 6. Reiniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# 7. Verificar
./scripts/verify_production_readiness.sh
```

### 8.3 Rotación de Logs

```bash
# Configurar logrotate
sudo nano /etc/logrotate.d/proyecto-semilla
```

```
/home/proyecto_semilla/proyecto-semilla/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 proyecto_semilla proyecto_semilla
    sharedscripts
    postrotate
        docker-compose -f /home/proyecto_semilla/proyecto-semilla/docker-compose.prod.yml kill -s USR1 backend
    endscript
}
```

### 8.4 Monitoreo

#### Health Checks Automáticos

```bash
# Crear script de monitoreo
nano /home/proyecto_semilla/health_check.sh
```

```bash
#!/bin/bash
# Health check script

URL="https://tu-dominio.com/api/v1/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ System healthy"
    exit 0
else
    echo "❌ System unhealthy (HTTP $RESPONSE)"
    # Enviar alerta (email, Slack, etc.)
    exit 1
fi
```

```bash
chmod +x /home/proyecto_semilla/health_check.sh

# Agregar a cron (cada 5 minutos)
*/5 * * * * /home/proyecto_semilla/health_check.sh
```

---

## 9. Troubleshooting

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Verificar configuración
docker-compose -f docker-compose.prod.yml config

# Reconstruir desde cero
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Problema: Error de conexión a base de datos

```bash
# Verificar que DB esté corriendo
docker-compose -f docker-compose.prod.yml ps db

# Ver logs de base de datos
docker-compose -f docker-compose.prod.yml logs db

# Conectar manualmente para probar
docker-compose -f docker-compose.prod.yml exec db psql -U admin -d proyecto_semilla
```

### Problema: HTTPS no funciona

```bash
# Verificar certificados
ls -la docker/nginx/ssl/

# Ver logs de Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Probar configuración de Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### Problema: Rendimiento lento

```bash
# Ver uso de recursos
docker stats

# Aumentar recursos en docker-compose.prod.yml
# Agregar más workers al backend
# Configurar Redis con más memoria
```

---

## 📚 Recursos Adicionales

- **Documentación API:** `https://tu-dominio.com/api/v1/docs`
- **Repositorio:** https://github.com/your-org/proyecto-semilla
- **Issues:** https://github.com/your-org/proyecto-semilla/issues
- **Auditoría de Producción:** [AUDITORIA_PRODUCCION_COMPLETA.md](./AUDITORIA_PRODUCCION_COMPLETA.md)

---

## ⚠️ Notas de Seguridad

1. **Nunca commitear `.env.production` al repositorio**
2. **Cambiar credenciales por defecto inmediatamente**
3. **Mantener Docker y dependencias actualizadas**
4. **Configurar backups automáticos desde el día 1**
5. **Monitorear logs de seguridad regularmente**
6. **Usar HTTPS en producción (obligatorio)**
7. **Configurar rate limiting apropiado**
8. **Habilitar 2FA para usuarios admin (futuro)**

---

**¡Felicitaciones! Tu instancia de Proyecto Semilla está lista para producción.** 🎉

Para soporte, abre un issue en GitHub o consulta la documentación completa en `/docs`.
