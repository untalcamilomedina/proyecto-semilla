# Análisis de Riesgos de Seguridad - Usuarios Hardcodeados

## Resumen Ejecutivo

Se han identificado usuarios hardcodeados en el sistema que representan riesgos de seguridad significativos. Estos usuarios se crean automáticamente durante la inicialización y tienen contraseñas predeterminadas que podrían ser explotadas.

## Usuarios Hardcodeados Identificados

### 1. admin@example.com
- **Ubicación**: `backend/app/initial_data.py`
- **Contraseña**: `admin123` (hardcodeada)
- **Propósito**: Usuario administrador por defecto
- **Riesgo**: Alto - Contraseña expuesta en código fuente

### 2. admin@proyectosemilla.dev
- **Ubicación**: `backend/scripts/seed_data.py`
- **Contraseña**: Configurable via `SEED_ADMIN_PASSWORD` (por defecto: `ChangeMeSecure123!`)
- **Propósito**: Super administrador del sistema
- **Riesgo**: Medio-Alto - Contraseña por defecto insegura

### 3. demo@demo-company.com
- **Ubicación**: `backend/scripts/seed_data.py`
- **Contraseña**: Configurable via `SEED_DEMO_PASSWORD` (por defecto: `demo123`)
- **Propósito**: Usuario de demostración
- **Riesgo**: Medio - Contraseña por defecto simple

## Vulnerabilidades Identificadas

### 1. Exposición de Credenciales
**Severidad**: Crítica
**Descripción**: Las contraseñas aparecen en múltiples archivos:
- Código fuente (`initial_data.py`)
- Scripts de instalación
- Variables de entorno de ejemplo
- Documentación pública
- Tests automatizados

**Impacto**: Un atacante podría obtener acceso no autorizado al sistema usando estas credenciales conocidas.

### 2. Lógica de Exclusión Insegura
**Severidad**: Alta
**Descripción**: La función `get_setup_status()` en `auth.py` excluye estos usuarios del conteo de "usuarios reales":

```python
hardcoded_emails = ["admin@proyectosemilla.dev", "demo@demo-company.com", "admin@example.com"]
```

**Riesgo**: Esta lógica podría ser usada para:
- Bypass de validaciones de configuración inicial
- Manipulación del estado del sistema
- Ataques de enumeración de usuarios

### 3. Creación Automática sin Validación
**Severidad**: Media
**Descripción**: Los usuarios se crean automáticamente sin:
- Verificación robusta de existencia previa
- Validación de seguridad de contraseñas
- Auditoría de creación

### 4. Dependencias Difusas
**Severidad**: Media
**Descripción**: Los usuarios hardcodeados están referenciados en:
- 31+ archivos diferentes
- Scripts de instalación automática
- Tests que dependen de credenciales específicas
- Documentación que expone las credenciales

## Recomendaciones de Mitigación

### Inmediatas (Alta Prioridad)

1. **Eliminar Contraseñas Hardcodeadas**
   - Reemplazar contraseñas fijas con generación segura
   - Implementar validación de complejidad de contraseñas
   - Forzar cambio de contraseña en primer login

2. **Implementar Variables de Entorno Obligatorias**
   - Hacer que `SEED_ADMIN_PASSWORD` y `SEED_DEMO_PASSWORD` sean obligatorias
   - Validar que no usen valores por defecto en producción

3. **Mejorar Lógica de Exclusión**
   - Implementar una lista configurable de usuarios del sistema
   - Agregar validaciones adicionales para prevenir bypass
   - Documentar claramente el propósito de la exclusión

### Mediano Plazo

4. **Implementar Sistema de Usuarios del Sistema**
   - Crear tabla separada para usuarios del sistema
   - Implementar flags de sistema en lugar de emails hardcodeados
   - Mejorar separación entre usuarios reales y del sistema

5. **Auditoría y Monitoreo**
   - Implementar logging detallado de creación de usuarios del sistema
   - Agregar alertas para uso de contraseñas por defecto
   - Monitorear intentos de login con credenciales conocidas

### Largo Plazo

6. **Migración Completa**
   - Desarrollar estrategia de migración para eliminar dependencias
   - Implementar sistema de configuración inicial más robusto
   - Crear usuarios administrativos de forma interactiva durante setup

## Plan de Implementación

### Fase 1: Mitigaciones Inmediatas
- [ ] Eliminar contraseñas hardcodeadas de `initial_data.py`
- [ ] Hacer variables de entorno obligatorias
- [ ] Implementar validación de contraseñas seguras
- [ ] Mejorar lógica de exclusión en `get_setup_status()`

### Fase 2: Mejoras de Seguridad
- [ ] Crear tabla de usuarios del sistema
- [ ] Implementar flags de sistema
- [ ] Agregar auditoría de creación de usuarios
- [ ] Actualizar documentación

### Fase 3: Migración Completa
- [ ] Desarrollar estrategia de eliminación
- [ ] Actualizar todos los scripts dependientes
- [ ] Implementar setup interactivo
- [ ] Remover referencias hardcodeadas

## Conclusión

Los usuarios hardcodeados representan un riesgo de seguridad significativo que requiere atención inmediata. La implementación de las mitigaciones propuestas reducirá considerablemente la superficie de ataque y mejorará la postura de seguridad general del sistema.