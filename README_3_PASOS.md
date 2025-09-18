# 🌱 Proyecto Semilla - 3 Pasos para Empezar

## ¡Como WordPress pero para Enterprise!

### 🚀 PASO 1: Levantar la plataforma
```bash
git clone https://github.com/proyecto-semilla/proyecto-semilla.git
cd proyecto-semilla
./start.sh
```

### 🌐 PASO 2: Acceder al sistema
Abre tu navegador y ve a: **http://localhost:7701**

### ⚙️ PASO 3: Configuración inicial
- **Si es primera vez**: Verás el formulario de "Configuración Inicial"
- **Crea tu superadministrador**: Nombre, apellido, email y contraseña
- **¡Listo!** Tu plataforma estará configurada

## 🔐 Inicio de Sesión
Después de la configuración inicial:
- **Email**: El que configuraste
- **Contraseña**: La que configuraste

## 🎯 ¿Qué incluye?
- ✅ **Backend FastAPI** con autenticación JWT
- ✅ **Base de datos PostgreSQL** multi-tenant
- ✅ **Frontend Next.js** moderno y responsivo
- ✅ **Sistema Vibecoding** (MCP Server)
- ✅ **Dashboard administrativo** completo
- ✅ **API RESTful** con 49+ endpoints

## 🆘 ¿Problemas?
```bash
# Ver logs
docker-compose logs

# Reiniciar
docker-compose restart

# Limpiar y empezar de nuevo
docker-compose down --volumes
./start.sh
```

---
**¡Feliz Vibecoding!** 🚀