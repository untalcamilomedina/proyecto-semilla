---
name: debug-protocol
description: Protocolo profesional para análisis de raíz, corrección de errores y eliminación de deuda técnica. Evita parches temporales.
author: AppNotion Engineering
version: 1.0.0
---

# Skill: Protocolo de Depuración Profesional (Root Cause Analysis)

Esta skill define el estándar para abordar errores ("bugs") de forma sistémica, evitando suposiciones y soluciones temporales ("parches").

## Prerrequisitos

- [ ] Acceso completo a logs (StackTrace).
- [ ] Acceso al código fuente y configuración del entorno.
- [ ] Capacidad de reproducción del error.

## Proceso de Ejecución

### Fase 1: Recolección de Evidencia (No Suponer)

Antes de escribir una sola línea de código:

1.  **Leer el StackTrace completo**: No solo la última línea. Buscar el origen real.
2.  **Auditar el Entorno**: Validar versiones (`python --version`, `npm -v`) y variables de entorno (`printenv`).
3.  **Verificar Paths**: Usar `ls -R` o `find` para asegurar que los archivos importados existen donde se espera.

### Fase 2: Hipótesis Fundamentada

Formular el problema en formato: _"El sistema falla en [Punto X] porque espera [Condición A] pero recibe [Condición B], causado por [Origen Root]"_.

**Ejemplo de Análisis:**

> _Error:_ `ModuleNotFoundError: No module named 'config'`
> _Contexto:_ `manage.py` está en raíz, `config` está en `src/config`.
> _Causa Raíz:_ Python no busca módulos en subdirectorios (`src`) automáticamete a menos que estén en `PYTHONPATH`.
> _Solución Profesional:_ Agregar `src` al `sys.path` dinámicamente en el punto de entrada, en lugar de mover carpetas desordenadamente.

### Fase 3: Implementación de la Solución (Clean Code)

1.  **Mínimo Impacto**: La solución debe ser quirúrgica.
2.  **Sin Hardcoding**: Usar `pathlib` o rutas relativas, nunca rutas absolutas de usuario.
3.  **Documentación**: Comentar _por qué_ se hace el cambio si no es obvio.

### Fase 4: Verificación y No Regresión

1.  Ejecutar el comando que fallaba.
2.  Verificar que no haya roto funcionalidades adyacentes.

## Checklist de Calidad

- [ ] ¿He identificado la causa raíz o solo estoy ocultando el síntoma?
- [ ] ¿La solución funciona en local y en producción (Docker/CI)?
- [ ] ¿He eliminado código muerto o configs obsoletas relacionadas?

## Errores Comunes a Evitar

- **"Funciona en mi máquina"**: Validar siempre paths relativos.
- **Ignorar Errores**: Usar `try/except pass` es inaceptable.
- **Hardcoding de Puertos/URLs**: Usar siempre variables de entorno.
