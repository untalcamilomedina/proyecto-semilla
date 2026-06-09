---
name: skill-generator
description: Meta-skill para crear nuevas skills siguiendo el formato Antigravity. Pregunta si es global o específica de proyecto.
author: Mayordomos Dev Team
version: 1.0.0
---

# Skill: Generador de Skills

Esta meta-skill guía la creación de nuevas skills para agentes AI, siguiendo el formato Antigravity y las mejores prácticas aprendidas.

## Pregunta Inicial

> **¿La skill es GLOBAL o específica de un PROYECTO?**

| Tipo | Ubicación | Uso |
|------|-----------|-----|
| **Global** | `~/.gemini/antigravity/skills/` | Disponible en todos los proyectos |
| **Proyecto** | `.agent/skills/` | Solo para este proyecto |

## Proceso de Creación

### Paso 1: Definir Propósito

Responder estas preguntas:

1. **¿Qué problema resuelve?**
   - Ejemplo: "Evitar que se repitan errores de i18n"

2. **¿Cuándo se usará?**
   - Ejemplo: "Cada vez que se crea una nueva página"

3. **¿Qué conocimiento encapsula?**
   - Patrones de código
   - Convenciones del proyecto
   - Checklists de verificación
   - Templates reutilizables

4. **¿Depende de otras skills?**
   - Ejemplo: `new-page` puede requerir `i18n-keys` primero

### Paso 2: Estructura de Carpetas

```bash
# Para skill de PROYECTO
mkdir -p .agent/skills/nombre-skill/{examples,resources}

# Para skill GLOBAL
mkdir -p ~/.gemini/antigravity/skills/nombre-skill/{examples,resources}
```

### Paso 3: Crear SKILL.md

El archivo principal debe tener:

```markdown
---
name: nombre-skill
description: Descripción clara y concisa (1 línea)
author: Tu Nombre o Equipo
version: 1.0.0
---

# Skill: Título Descriptivo

Párrafo introductorio explicando qué hace la skill y cuándo usarla.

## Prerrequisitos

- Qué se necesita antes de usar esta skill
- Otras skills que deben ejecutarse primero

## Proceso

### Paso 1: Título del Paso
Explicación detallada...

### Paso 2: Título del Paso
Explicación detallada...

## Templates

```code
// Template reutilizable con comentarios
```

## Checklist

- [ ] Item verificable 1
- [ ] Item verificable 2
- [ ] Item verificable 3

## Errores Comunes

### Error: Descripción
**Causa:** Por qué ocurre
**Solución:** Cómo resolverlo

## Referencias

- [Documento relacionado](./ruta/archivo.md)
- [Documentación externa](https://url)
```

### Paso 4: Agregar Ejemplos

Crear archivos en `examples/` con código real:

```
examples/
├── simple-example.tsx      # Caso básico
├── advanced-example.tsx    # Caso complejo
└── edge-case.tsx           # Casos especiales
```

### Paso 5: Documentar en README

Actualizar el README del directorio de skills:

```markdown
| [nombre-skill](./nombre-skill/SKILL.md) | Descripción breve | Tier |
```

## Mejores Prácticas

### 1. Contenido Específico vs Genérico

| Incluir | Evitar |
|---------|--------|
| Paths exactos del proyecto | Instrucciones genéricas |
| Templates copiables | Pseudo-código |
| Checklists verificables | Listas de sugerencias |
| Ejemplos reales del codebase | Ejemplos hipotéticos |
| Referencias a archivos | Referencias vagas |

### 2. Nivel de Detalle

- **Demasiado breve**: El agente tiene que adivinar
- **Demasiado largo**: El agente se pierde
- **Ideal**: Suficiente para que el agente ejecute sin preguntar

### 3. Estructura Consistente

Todas las skills deben tener:

1. **Frontmatter YAML** con name, description, author, version
2. **Introducción** de 1-2 párrafos
3. **Prerrequisitos** si aplican
4. **Proceso** paso a paso
5. **Templates** copiables
6. **Checklist** de verificación
7. **Referencias** a documentación

### 4. Testing de la Skill

Antes de finalizar:

1. Simular uso de la skill paso a paso
2. Verificar que los paths son correctos
3. Verificar que los templates compilan
4. Verificar que el checklist es completo

## Template Completo de SKILL.md

```markdown
---
name: mi-nueva-skill
description: Descripción en una línea de lo que hace
author: Nombre del Autor
version: 1.0.0
---

# Skill: Nombre Legible de la Skill

Esta skill [verbo en presente] [qué hace] para [beneficio].

## Prerrequisitos

Antes de usar esta skill:

- [ ] Prerrequisito 1
- [ ] Prerrequisito 2

## Cuándo Usar

Usar esta skill cuando:
- Situación 1
- Situación 2

NO usar cuando:
- Situación que no aplica

## Proceso

### Paso 1: Título Descriptivo

Explicación de qué hacer en este paso.

```código
// Ejemplo de código
```

### Paso 2: Título Descriptivo

Explicación del siguiente paso.

| Campo | Valor | Descripción |
|-------|-------|-------------|
| campo1 | valor1 | qué significa |
| campo2 | valor2 | qué significa |

## Templates

### Template Principal

```código
// Template completo y copiable
// Con comentarios explicativos
```

### Template Alternativo (si aplica)

```código
// Variación para casos específicos
```

## Checklist de Verificación

### Obligatorio
- [ ] Item crítico 1
- [ ] Item crítico 2
- [ ] Item crítico 3

### Recomendado
- [ ] Item nice-to-have 1
- [ ] Item nice-to-have 2

## Errores Comunes

### Error: "Mensaje de error"

**Causa:** Explicación de por qué ocurre

**Solución:**
```código
// Cómo solucionarlo
```

### Error: "Otro error común"

**Causa:** Explicación

**Solución:** Pasos para resolver

## Referencias

- [Archivo relacionado](./ruta/al/archivo)
- [Documentación](./docs/documento.md)
- [Recurso externo](https://url)

---

*Última actualización: YYYY-MM-DD*
```

## Aprendizajes de Esta Sesión

### Lo que Funcionó Bien

1. **Referencias a archivos reales**: Los paths exactos ayudan al agente
2. **Ejemplos del codebase**: Más útil que ejemplos genéricos
3. **Tablas de resumen**: Fáciles de escanear
4. **Checklists**: Verificación paso a paso
5. **Secciones de errores comunes**: Previenen problemas

### Lo que Evitar

1. **Instrucciones vagas**: "Hacer algo similar a..."
2. **Ejemplos incompletos**: Código que no compila
3. **Falta de contexto**: No explicar el "por qué"
4. **Skills demasiado amplias**: Mejor varias skills pequeñas
5. **Dependencias no documentadas**: "Primero necesitas..."

## Checklist de Creación de Skill

### Estructura
- [ ] Carpeta creada en ubicación correcta
- [ ] SKILL.md con frontmatter YAML
- [ ] Carpeta examples/ si hay ejemplos
- [ ] README del directorio actualizado

### Contenido
- [ ] Introducción clara
- [ ] Prerrequisitos documentados
- [ ] Proceso paso a paso
- [ ] Al menos un template copiable
- [ ] Checklist de verificación
- [ ] Referencias a archivos reales

### Calidad
- [ ] Paths verificados
- [ ] Templates probados
- [ ] Ejemplos que compilan
- [ ] Consistente con otras skills

## Referencias

- [Antigravity Skills Docs](https://antigravity.google/docs/skills)
- [README de Skills](../README.md)
- [Ejemplos de skills existentes](../)
