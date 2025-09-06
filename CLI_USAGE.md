# 🧠 Vibecoding Discovery CLI - Guía de Uso

**Architecture Discovery Engine - Interfaz de Línea de Comandos en Español**

## 🚀 Instalación y Configuración

### Requisitos
- Python 3.8+
- Proyecto Semilla clonado
- Dependencias instaladas: `pip install sqlalchemy fastapi jose passlib pathlib`

### Instalación Rápida
```bash
cd proyecto-semilla
chmod +x vibecoding-discovery
./vibecoding-discovery version  # Verificar instalación
```

## 📋 Comandos Disponibles

### 🔍 `analyze` - Análisis de Arquitectura

Analiza cualquier proyecto de software y genera reportes detallados.

```bash
# Sintaxis básica
./vibecoding-discovery analyze [PROYECTO] [OPCIONES]

# Ejemplos
./vibecoding-discovery analyze .                    # Proyecto actual
./vibecoding-discovery analyze /mi/proyecto         # Proyecto específico
./vibecoding-discovery analyze . --detallado       # Con progreso detallado
./vibecoding-discovery analyze . --guardar         # Guardar resultados
./vibecoding-discovery analyze . --formato json    # Solo formato JSON
```

#### Opciones del Comando Analyze

| Opción | Alias | Descripción |
|--------|-------|-------------|
| `--detallado` | `-v` | Muestra progreso detallado durante análisis |
| `--guardar` | `-s` | Guarda resultados en archivos |
| `--salida DIR` | `-o DIR` | Directorio personalizado para guardar |
| `--formato FORMAT` | `-f FORMAT` | Formato: `json`, `md`, `txt`, `todos` |
| `--idioma LANG` | | Idioma: `es` (español), `en` (inglés) |
| `--incluir-seguridad` | | Incluir análisis de seguridad (activado por defecto) |
| `--incluir-patrones` | | Incluir reconocimiento de patrones (activado por defecto) |

### 🚀 `demo` - Demostración Interactiva

Ejecuta demostración usando el Proyecto Semilla como ejemplo.

```bash
# Sintaxis básica
./vibecoding-discovery demo [OPCIONES]

# Ejemplos
./vibecoding-discovery demo                    # Demo automático
./vibecoding-discovery demo --interactivo     # Demo con menú paso a paso
./vibecoding-discovery demo --guardar-demo    # Guardar resultados de demo
```

### 📋 `version` - Información de Versión

```bash
./vibecoding-discovery version
```

Muestra versión del sistema y componentes instalados.

### ❓ `ayuda` - Sistema de Ayuda

```bash
# Ayuda general
./vibecoding-discovery ayuda

# Ayuda específica por tema
./vibecoding-discovery ayuda analyze     # Comando analyze
./vibecoding-discovery ayuda demo        # Comando demo
./vibecoding-discovery ayuda formatos    # Formatos de salida
./vibecoding-discovery ayuda ejemplos    # Ejemplos prácticos
```

## 📊 Formatos de Salida

### 📄 Formatos Disponibles

| Formato | Descripción | Uso Recomendado |
|---------|-------------|-----------------|
| `json` | Datos estructurados | APIs, automatización, análisis programático |
| `md` | Reporte Markdown | Documentación, GitHub, wikis |
| `txt` | Texto simple | Terminal, logs, scripts |
| `todos` | Los 3 anteriores | Uso general (por defecto) |

### 📁 Estructura de Archivos Generados

```
architecture_analysis_results/
├── 📊 architecture_analysis.json      # Datos estructurados completos
├── 📝 architecture_report.md          # Reporte ejecutivo elegante  
└── 📄 architecture_summary.txt        # Resumen simple para terminal
```

## 🎯 Casos de Uso Prácticos

### 1. 🔍 Análisis Rápido para Desarrolladores

```bash
./vibecoding-discovery analyze .
```
- Análisis inmediato del proyecto actual
- Resultados mostrados en pantalla
- Perfecto para evaluación rápida

### 2. 📊 Auditoría Completa de Proyecto

```bash
./vibecoding-discovery analyze /ruta/proyecto --detallado --guardar --salida ./auditoria
```
- Análisis exhaustivo con progreso detallado
- Archivos guardados en directorio específico
- Ideal para auditorías formales

### 3. 🤖 Integración CI/CD

```bash
./vibecoding-discovery analyze . --formato json --salida ./reports
```
- Solo datos JSON para procesamiento automatizado
- Sin salida verbose para pipelines
- Perfecto para integración con herramientas

### 4. 📈 Evaluación de Arquitectura Legacy

```bash
./vibecoding-discovery analyze /legacy-app --detallado --guardar
```
- Análisis detallado de aplicaciones existentes
- Identificación de deuda técnica
- Roadmap de modernización

### 5. 🎓 Demo para Stakeholders

```bash
./vibecoding-discovery demo --interactivo
```
- Demostración paso a paso
- Perfecto para presentaciones técnicas
- Muestra capacidades del sistema

## 🧠 Qué Analiza el Sistema

### 📊 Base de Datos
- ✅ **Modelos SQLAlchemy** y relaciones
- ✅ **Patrones multi-tenant** con RLS (Row-Level Security)
- ✅ **UUIDs** y esquemas de claves primarias
- ✅ **Índices** y optimizaciones detectadas

### 🔌 API Backend
- ✅ **Endpoints FastAPI** con métodos HTTP
- ✅ **Patrones RESTful** y versionado de API
- ✅ **Middleware personalizado** y dependencias
- ✅ **Documentación OpenAPI** automática

### 🎨 Frontend
- ✅ **Componentes React/Next.js** y TypeScript
- ✅ **Sistemas de estilos** (Tailwind, CSS Modules)
- ✅ **Gestión de estado** (Context, Zustand, Redux)
- ✅ **Hooks personalizados** y patrones

### 🔒 Seguridad
- ✅ **Autenticación JWT** y refresh tokens
- ✅ **Control de acceso** basado en roles (RBAC)
- ✅ **Row-Level Security** (RLS) para multi-tenancy
- ✅ **Análisis de vulnerabilidades** y recomendaciones

### 🧠 Patrones Arquitectónicos
- ✅ **Repository Pattern**, MVC, Factory, Observer
- ✅ **Microservices**, Multi-Tenant, CQRS
- ✅ **Anti-patrones** y code smells
- ✅ **Recomendaciones** contextualizadas con IA

## 📈 Sistema de Puntuación

### Métricas Principales
- **Score General**: 0-10 (arquitectura overall)
- **Score de Seguridad**: 0-100 (modelo de seguridad)
- **Score de Mantenibilidad**: 0-10 (calidad de código)
- **Score de Consistencia**: 0-10 (patrones consistentes)

### Interpretación de Scores
- **8-10**: Excelente arquitectura, listo para producción
- **6-8**: Buena arquitectura, pocas mejoras necesarias
- **4-6**: Arquitectura aceptable, mejoras recomendadas
- **0-4**: Arquitectura problemática, refactoring necesario

## 🌐 Internacionalización

### Idiomas Soportados
- 🇪🇸 **Español**: Idioma primario (por defecto)
- 🇺🇸 **Inglés**: Soporte secundario

### Cambiar Idioma
```bash
./vibecoding-discovery analyze . --idioma en  # Reportes en inglés
./vibecoding-discovery analyze . --idioma es  # Reportes en español (defecto)
```

## 🛠️ Configuración Avanzada

### Variables de Entorno (Opcional)
```bash
export VIBECODING_LOCALE=es          # Idioma por defecto
export VIBECODING_OUTPUT_DIR=./out   # Directorio de salida por defecto
export VIBECODING_VERBOSE=true       # Modo detallado por defecto
```

### Personalización de Análisis
El sistema detecta automáticamente:
- Estructura de carpetas del proyecto
- Tecnologías utilizadas
- Patrones de naming
- Configuraciones específicas del framework

## 🔧 Troubleshooting

### Problemas Comunes

#### Error: "Comando no encontrado"
```bash
chmod +x vibecoding-discovery  # Hacer el script ejecutable
```

#### Error: "Módulo no encontrado"
```bash
pip install sqlalchemy fastapi jose passlib pathlib
```

#### Error: "Ruta no existe"
```bash
./vibecoding-discovery analyze /ruta/absoluta/correcta
```

#### Score de seguridad muy bajo
- El sistema es conservador con seguridad
- 1400+ "vulnerabilidades menores" pueden ser falsos positivos
- Score 50/100 es típico para proyectos reales

### Logs de Debug
```bash
./vibecoding-discovery analyze . --detallado  # Ver progreso completo
```

## 🎯 Roadmap y Futuras Características

### Próximas Versiones
- 🔮 **Análisis de Dockerfile** y configuraciones de despliegue
- 🔮 **Detección de microservicios** inter-conectados  
- 🔮 **Análisis de performance** y bottlenecks
- 🔮 **Integración con GitHub Actions** nativa
- 🔮 **Dashboard web** con visualizaciones interactivas
- 🔮 **Soporte para Vue.js**, Angular, Python Flask

### Contribuir
El Vibecoding Discovery CLI es parte del Proyecto Semilla. Para contribuir:
1. Crea issues en el repositorio
2. Propón nuevos analizadores
3. Mejora traducciones existentes
4. Comparte casos de uso

---

## 📞 Soporte

- **Documentación completa**: [./core/discovery/README.md](./core/discovery/README.md)
- **Arquitectura técnica**: [./core/discovery/ARCHITECTURE.md](./core/discovery/ARCHITECTURE.md)
- **Issues y bugs**: GitHub Issues del proyecto
- **Ejemplos**: [./core/discovery/examples/](./core/discovery/examples/)

---

## 🏆 Características Destacadas

### 🎯 Único en el Mercado
- **Primer CLI de análisis arquitectónico completamente en español**
- **IA especializada en patrones de desarrollo latinoamericano**  
- **Enfoque en stack moderno (FastAPI + React)**

### 📊 Enterprise-Ready
- **Reportes ejecutivos profesionales**
- **Métricas standardizadas de calidad**
- **Integración con pipelines CI/CD**
- **Análisis de riesgos priorizados**

### 🧠 Inteligencia Avanzada
- **Reconocimiento de patrones con ML**
- **Análisis predictivo de problemas futuros**
- **Recomendaciones contextualizadas por proyecto**
- **Detección automática de anti-patrones**

---

*🤖 Generado por Vibecoding Discovery CLI v1.0.0*  
*🧠 Architecture Discovery Engine - El futuro del análisis de arquitectura en español*