# 🔧 Scripts - Proyecto Semilla

Este directorio contiene scripts de automatización, instalación y mantenimiento del proyecto.

## 📋 Scripts Disponibles (Planeados)

### 🚀 Instalación y Setup
- [`install.py`](#installpy) - Instalador interactivo principal
- [`setup-dev.sh`](#setup-devsh) - Configuración para desarrollo local
- [`setup-prod.sh`](#setup-prodsh) - Configuración para producción
- [`verify-install.py`](#verify-installpy) - Verificar instalación correcta

### 🔄 Mantenimiento y Actualizaciones
- [`update.sh`](#updatesh) - Script de actualización automática
- [`backup.py`](#backuppy) - Respaldo de base de datos y archivos
- [`restore.py`](#restorepy) - Restaurar desde backup
- [`health-check.py`](#health-checkpy) - Verificar salud del sistema

### 🗄️ Base de Datos
- [`migrate.py`](#migratepy) - Ejecutar migraciones
- [`seed-data.py`](#seed-datapy) - Poblar con datos de ejemplo
- [`reset-db.py`](#reset-dbpy) - Resetear base de datos completa
- [`analyze-db.py`](#analyze-dbpy) - Análisis de performance de DB

### 🧪 Testing y Calidad
- [`run-tests.sh`](#run-testssh) - Ejecutar todos los tests
- [`lint-fix.sh`](#lint-fixsh) - Ejecutar linting y auto-fix
- [`security-scan.py`](#security-scanpy) - Scan de vulnerabilidades
- [`performance-test.py`](#performance-testpy) - Tests de performance

### 📦 Despliegue
- [`deploy.sh`](#deploysh) - Despliegue automatizado
- [`rollback.sh`](#rollbacksh) - Rollback a versión anterior
- [`docker-build.sh`](#docker-buildsh) - Build de imágenes Docker
- [`k8s-deploy.py`](#k8s-deploypy) - Despliegue en Kubernetes

---

## 📝 Documentación Detallada

### `install.py`

**Descripción**: Script de instalación interactiva que guía al usuario a través de la configuración inicial.

**Características**:
- Configuración guiada del archivo `.env`
- Validación de dependencias (Docker, PostgreSQL, etc.)
- Creación automática de base de datos
- Setup del primer superadministrador
- Verificación de conectividad
- Rollback automático en caso de error

**Uso**:
```bash
python scripts/install.py

# Opciones avanzadas
python scripts/install.py --config-file=custom.env
python scripts/install.py --skip-db-creation
python scripts/install.py --production
```

**Flujo de Instalación**:
1. Verificar prerrequisitos
2. Configurar variables de entorno
3. Crear base de datos y usuario
4. Ejecutar migraciones iniciales
5. Crear superadministrador
6. Poblar datos básicos
7. Verificar instalación
8. Mostrar información de acceso

### `setup-dev.sh`

**Descripción**: Configuración rápida para entorno de desarrollo local.

**Características**:
- Instalar dependencias de desarrollo
- Configurar pre-commit hooks
- Levantar servicios Docker (PostgreSQL, Redis)
- Configurar variables de entorno de desarrollo
- Poblar con datos de ejemplo

**Uso**:
```bash
./scripts/setup-dev.sh

# Con datos de ejemplo específicos
./scripts/setup-dev.sh --seed=church-example
./scripts/setup-dev.sh --seed=school-example
```

### `update.sh`

**Descripción**: Actualización automática del sistema con verificaciones de seguridad.

**Características**:
- Backup automático antes de actualizar
- Git pull con verificación de firma
- Ejecutar migraciones de base de datos
- Actualizar dependencias
- Reiniciar servicios
- Verificar que la actualización fue exitosa
- Rollback automático si algo falla

**Uso**:
```bash
./scripts/update.sh

# Actualización específica a versión
./scripts/update.sh --version=v0.2.0

# Actualización forzada (omitir verificaciones)
./scripts/update.sh --force
```

**Proceso de Actualización**:
1. Crear backup completo
2. Verificar nueva versión
3. Descargar cambios
4. Ejecutar migraciones
5. Actualizar dependencias
6. Reiniciar servicios
7. Ejecutar health checks
8. Confirmar éxito o rollback

### `backup.py`

**Descripción**: Sistema de backup completo con compresión y encriptación.

**Características**:
- Backup de base de datos PostgreSQL
- Backup de archivos de configuración
- Backup de uploads/media
- Compresión gzip
- Encriptación opcional
- Rotación automática de backups antiguos
- Verificación de integridad

**Uso**:
```bash
# Backup completo
python scripts/backup.py

# Solo base de datos
python scripts/backup.py --db-only

# Con encriptación
python scripts/backup.py --encrypt --key-file=backup.key

# A ubicación específica
python scripts/backup.py --output=/path/to/backups/
```

### `health-check.py`

**Descripción**: Verificación completa de la salud del sistema.

**Características**:
- Verificar conectividad de base de datos
- Comprobar servicios Docker
- Validar APIs endpoints
- Verificar espacio en disco
- Comprobar memoria y CPU
- Validar certificados SSL
- Generar reporte detallado

**Uso**:
```bash
# Check básico
python scripts/health-check.py

# Check detallado con métricas
python scripts/health-check.py --detailed

# Solo verificar componente específico
python scripts/health-check.py --component=database
python scripts/health-check.py --component=api

# Output en formato JSON
python scripts/health-check.py --format=json
```

### `seed-data.py`

**Descripción**: Poblar la base de datos with datos de ejemplo realistas.

**Características**:
- Múltiples datasets (iglesias, escuelas, empresas)
- Datos realistas pero ficticios
- Configuración de tenants de ejemplo
- Usuarios con diferentes roles
- Relaciones complejas entre entidades
- Modo desarrollo vs producción

**Uso**:
```bash
# Dataset básico
python scripts/seed-data.py

# Dataset específico
python scripts/seed-data.py --dataset=church
python scripts/seed-data.py --dataset=school
python scripts/seed-data.py --dataset=enterprise

# Limpiar y re-poblar
python scripts/seed-data.py --clean-first

# Número específico de registros
python scripts/seed-data.py --tenants=5 --users-per-tenant=20
```

### `security-scan.py`

**Descripción**: Análisis automático de seguridad del proyecto.

**Características**:
- Scan de dependencias con vulnerabilidades conocidas
- Análisis estático de código
- Verificar configuración de seguridad
- Comprobar secrets hardcodeados
- Validar configuraciones Docker
- Generar reporte de seguridad

**Uso**:
```bash
# Scan completo
python scripts/security-scan.py

# Solo dependencias
python scripts/security-scan.py --dependencies-only

# Solo código fuente
python scripts/security-scan.py --code-only

# Generar reporte para CI/CD
python scripts/security-scan.py --ci --output=security-report.json
```

---

## 🏗️ Estructura Interna de Scripts

### 📁 Organización
```
scripts/
├── README.md                   # Este archivo
├── common/                     # Utilidades compartidas
│   ├── __init__.py
│   ├── logger.py              # Sistema de logging
│   ├── config.py              # Manejo de configuración
│   ├── database.py            # Utilidades de BD
│   ├── docker_utils.py        # Utilidades Docker
│   └── validators.py          # Validadores comunes
├── install/                   # Scripts de instalación
│   ├── install.py            # Script principal
│   ├── requirements.py       # Verificar dependencias
│   └── templates/            # Templates de configuración
│       ├── .env.template
│       └── docker-compose.template.yml
├── maintenance/              # Scripts de mantenimiento
│   ├── update.sh
│   ├── backup.py
│   ├── restore.py
│   └── health-check.py
├── database/                 # Scripts de base de datos
│   ├── migrate.py
│   ├── seed-data.py
│   ├── reset-db.py
│   └── seeds/               # Datasets
│       ├── church.json
│       ├── school.json
│       └── enterprise.json
├── testing/                 # Scripts de testing
│   ├── run-tests.sh
│   ├── lint-fix.sh
│   ├── security-scan.py
│   └── performance-test.py
├── deployment/              # Scripts de despliegue
│   ├── deploy.sh
│   ├── rollback.sh
│   ├── docker-build.sh
│   └── k8s-deploy.py
└── development/             # Scripts de desarrollo
    ├── setup-dev.sh
    ├── generate-api-docs.py
    └── create-migration.py
```

### 🔧 Utilidades Compartidas

**Logger (`common/logger.py`)**:
- Logging consistente en todos los scripts
- Múltiples niveles (DEBUG, INFO, WARNING, ERROR)
- Output a archivo y consola
- Formato estandarizado con timestamps

**Config (`common/config.py`)**:
- Lectura de variables de entorno
- Validación de configuración
- Valores por defecto sensatos
- Manejo seguro de secrets

**Database (`common/database.py`)**:
- Conexión segura a PostgreSQL
- Pool de conexiones
- Manejo de transacciones
- Utilidades para migraciones

## 📋 Convenciones

### 🐍 Python Scripts
- **Shebang**: `#!/usr/bin/env python3`
- **Encoding**: UTF-8 declarado
- **Docstrings**: Google style
- **Type hints**: Obligatorio para funciones públicas
- **Error handling**: Try/catch comprehensivo
- **Logging**: Usar el logger compartido

### 🐚 Bash Scripts
- **Shebang**: `#!/bin/bash`
- **Set options**: `set -euo pipefail`
- **Functions**: Para lógica reutilizable
- **Colors**: Para output amigable
- **Validation**: Verificar prerrequisitos

### 📝 Documentación
- **Header comment**: Descripción del script
- **Usage function**: Mostrar ayuda con `--help`
- **Examples**: Incluir ejemplos de uso
- **Exit codes**: Documentar códigos de salida

## 🛡️ Seguridad

### 🔒 Buenas Prácticas
- **Nunca** hardcodear passwords o secrets
- **Validar** todos los inputs del usuario
- **Usar** conexiones seguras (HTTPS, SSL)
- **Verificar** integridad de archivos descargados
- **Logging** de eventos de seguridad sin exponer secrets

### 🔍 Validaciones
- Verificar permisos antes de operaciones críticas
- Validar estructura de archivos de configuración
- Comprobar disponibilidad de puertos
- Verificar espacio en disco suficiente

---

## 🚀 Estado de Desarrollo

### ✅ Planeado para Fase 1 (v0.1.0-v0.3.0)
- [ ] `install.py` - Instalador interactivo
- [ ] `setup-dev.sh` - Setup de desarrollo
- [ ] `migrate.py` - Sistema de migraciones
- [ ] `seed-data.py` - Datos de ejemplo
- [ ] `health-check.py` - Verificación de sistema

### 🔮 Fases Futuras
- [ ] `update.sh` - Sistema de actualizaciones
- [ ] `backup.py` / `restore.py` - Sistema de respaldo
- [ ] `security-scan.py` - Análisis de seguridad
- [ ] `deploy.sh` - Despliegue automatizado
- [ ] `k8s-deploy.py` - Despliegue en Kubernetes

---

*Los scripts serán implementados progresivamente según las necesidades del proyecto y siguiendo las mejores prácticas de DevOps y automatización.*