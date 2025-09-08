# 🏗️ Instalador Proyecto Semilla

Script de instalación automática e interactiva para configurar Proyecto Semilla desde cero con mejores prácticas de seguridad.

## 🚀 Inicio Rápido

```bash
# Desde el directorio raíz del proyecto
cd backend/scripts
python3 install.py
```

## 📋 Lo que hace el instalador

### ✅ Verificación de Prerrequisitos
- Python 3.9+
- pip
- PostgreSQL
- Node.js 16+
- npm

### 📦 Instalación de Dependencias
- Instala dependencias Python desde `requirements.txt`
- Instala dependencias Node.js con `npm install`

### 🗄️ Configuración de Base de Datos
- Solicita configuración de PostgreSQL
- Crea la base de datos si no existe
- Ejecuta migraciones y crea tablas

### 🔐 Generación de Configuración Segura
- Genera JWT_SECRET único de 64 caracteres
- Crea contraseña segura para el super administrador
- Configura variables de entorno en `.env`

### 👑 Creación de Super Administrador
- Crea tenant inicial "Proyecto Semilla"
- Configura roles y permisos estándar
- Crea usuario super administrador con email configurable

### ✅ Validación de Instalación
- Verifica que todos los archivos estén en su lugar
- Valida la configuración generada

## 🎯 Uso Interactivo

El instalador es completamente interactivo y te guiará a través de cada paso:

1. **Verificación de prerrequisitos**: Se ejecuta automáticamente
2. **Instalación de dependencias**: Se ejecuta automáticamente
3. **Configuración de base de datos**: Solicita información de PostgreSQL
4. **Configuración de CORS**: Permite personalizar orígenes permitidos
5. **Información del admin**: Solicita nombre y email del super administrador

## 🔧 Configuración Personalizable

### Variables de Entorno Generadas
```env
# Base de datos
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proyecto_semilla
DB_USER=tu_usuario

# Backend
JWT_SECRET=secret_jwt_unico_64_chars
CORS_ORIGINS=http://localhost:3000,https://tu-dominio.com

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Seed Data
SEED_ADMIN_PASSWORD=password_seguro_generado
```

### Roles y Permisos Iniciales

**Super Admin** (`admin`):
- `users:read`, `users:write`, `users:delete`
- `tenants:read`, `tenants:write`
- `roles:read`, `roles:write`
- `articles:read`, `articles:write`, `articles:delete`
- `system:admin`

**Usuario Estándar** (`user`):
- `users:read`
- `tenants:read`
- `articles:read`, `articles:write`

## 🛡️ Mejores Prácticas de Seguridad

### Secrets Generados Automáticamente
- JWT_SECRET: 64 caracteres aleatorios
- Contraseña de admin: 16 caracteres aleatorios
- Todos los secrets usan caracteres seguros

### Validaciones Incluidas
- Verificación de fortaleza de JWT_SECRET
- Validación de formato de email
- Confirmación de conexión a base de datos

## 📊 Resumen de Instalación

Al finalizar, el instalador muestra:
- ✅ Tenant principal creado
- ✅ Super admin configurado
- ✅ Base de datos lista
- ✅ Configuración segura generada
- 🚀 Comandos para iniciar la aplicación

## 🔄 Próximos Pasos

Después de la instalación:

```bash
# Iniciar backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar frontend (en otra terminal)
cd frontend
npm run dev
```

Accede a `http://localhost:3000` y usa las credenciales del super admin.

## ⚠️ Notas Importantes

- **Guarda la contraseña del admin** en un lugar seguro
- **Cambia la contraseña** después del primer login
- **Configura variables de entorno** para producción
- **Revisa la documentación de seguridad** antes del despliegue

## 🐛 Solución de Problemas

### PostgreSQL no encontrado
```bash
# macOS con Homebrew
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Node.js versión incorrecta
```bash
# Instalar Node.js 16+ con nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### Error de permisos en base de datos
```sql
-- Crear usuario con permisos
CREATE USER proyecto_user WITH PASSWORD 'tu_password';
ALTER USER proyecto_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE proyecto_semilla TO proyecto_user;
```

## 📝 Personalización

El script se puede modificar para:
- Cambiar el nombre del tenant inicial
- Modificar roles y permisos por defecto
- Agregar configuración adicional
- Personalizar el flujo de instalación

## 🤝 Contribuir

Para mejorar el instalador:
1. Reporta issues con detalles del error
2. Sugiere mejoras en la UX
3. Envía PRs con mejoras de seguridad
4. Documenta casos de uso adicionales

---

**Proyecto Semilla** - Instalador Seguro y Automático 🏗️✨