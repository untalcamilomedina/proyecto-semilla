# 🎯 PROTOCOLO SOURCE OF TRUTH
## "Nunca más documentación desincronizada"

**Creado**: 7 de septiembre de 2025  
**Objetivo**: Prevenir discrepancias entre documentación y realidad técnica  
**Principio**: "El código funcionando es la única fuente de verdad"

---

## 🚨 **REGLAS FUNDAMENTALES**

### **REGLA #1: HIERARCHY OF TRUTH**
```
1. Código en main branch          ← AUTORIDAD MÁXIMA
2. Tests automatizados pasando    ← VALIDACIÓN FUNCIONAL  
3. `docker-compose up` exitoso    ← ESTADO DEPLOYABLE
4. Commits recientes              ← HISTORIA REAL
5. Documentación                  ← EXPLICACIÓN DEL CÓDIGO
```

### **REGLA #2: PROHIBICIONES ABSOLUTAS**
❌ **NUNCA documentar features no implementadas**  
❌ **NUNCA inventar métricas o fechas**  
❌ **NUNCA prometer funcionalidad sin código**  
❌ **NUNCA editar métricas manualmente**  

### **REGLA #3: VALIDATION FIRST**
✅ **SIEMPRE probar antes de documentar**  
✅ **SIEMPRE ejecutar daily-check.sh antes de commits**  
✅ **SIEMPRE demo funcional antes de "completado"**  
✅ **SIEMPRE métricas auto-generadas**

---

## 📋 **WORKFLOW OBLIGATORIO**

### **DAILY DEVELOPMENT CYCLE**
```bash
# 1. ANTES de empezar cualquier trabajo
./scripts/daily-check.sh

# 2. Durante desarrollo
# - Hacer cambios de código
# - Probar funcionalidad localmente

# 3. ANTES de cada commit
./scripts/pre-commit-reality.sh

# 4. Commit con mensaje descriptivo real
git commit -m "feat: implement user login form (validates email + password)"

# 5. DESPUÉS de commit
./scripts/update-status.sh
```

### **WEEKLY DEMO CYCLE**
```bash
# Cada viernes
./scripts/demo-prep.sh
# → Genera reporte de funcionalidad demostrable
# → Si algo falla, NO documentar como completado
```

---

## 🛡️ **QUALITY GATES**

### **GATE 1: Daily (Cada commit)**
```bash
# Must pass before any commit
- [ ] docker-compose up -d (no errors)
- [ ] Backend health check passes
- [ ] Frontend compiles without errors  
- [ ] Basic smoke tests pass
- [ ] CURRENT_STATUS.md updated automatically
```

### **GATE 2: Weekly (Cada viernes)**  
```bash
# Must pass before marking sprint progress
- [ ] Live demo of new functionality successful
- [ ] All code pushed to main branch
- [ ] Integration tests pass
- [ ] Documentation matches demonstrated functionality
```

### **GATE 3: Release (Antes de tags)**
```bash
# Must pass before any version tag
- [ ] Complete docker-compose up on fresh environment
- [ ] All endpoints responding correctly
- [ ] Frontend loads without console errors
- [ ] Release notes based ONLY on working features
```

---

## 🔧 **HERRAMIENTAS IMPLEMENTADAS**

### **1. CURRENT_STATUS.md - Auto-generated**
```markdown
# 📊 CURRENT STATUS - [AUTO-GENERATED]

## ✅ VERIFIED WORKING (Last tested: [DATE])
- Backend: [STATUS] (docker-compose logs backend)
- Frontend: [STATUS] (npm run build)
- Database: [STATUS] (health check)
- APIs: [COUNT] endpoints responding

## 🔢 REAL METRICS (Auto-calculated)  
- Lines of code: [AUTO_COUNT]
- Git commits: [AUTO_COUNT]
- Last successful demo: [AUTO_DATE]
- Docker services: [AUTO_STATUS]

## 🎯 NEXT PRIORITIES (Specific & Measurable)
- [ ] [TASK] - ETA: [REALISTIC_DATE]
- [ ] [TASK] - ETA: [REALISTIC_DATE]

---
*⚠️ WARNING: This file is auto-generated. Manual edits will be overwritten.*
```

### **2. Scripts de Validación**

#### **`scripts/daily-check.sh`**
```bash
#!/bin/bash
echo "🔍 DAILY REALITY CHECK - $(date)"

# Test basic services
docker-compose up -d --wait
DOCKER_STATUS=$?

# Health checks  
curl -s -f http://localhost:7777/health > /dev/null
BACKEND_STATUS=$?

# Update real metrics
LINES=$(find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs wc -l | tail -1 | awk '{print $1}')
COMMITS=$(git rev-list --count HEAD)

# Generate status report
cat > docs/CURRENT_STATUS.md << EOF
# 📊 CURRENT STATUS - $(date)

## ✅ SERVICE STATUS  
- Docker: $([ $DOCKER_STATUS -eq 0 ] && echo "✅ UP" || echo "❌ DOWN")
- Backend: $([ $BACKEND_STATUS -eq 0 ] && echo "✅ HEALTHY" || echo "❌ UNHEALTHY") 
- Last Check: $(date)

## 🔢 REAL METRICS
- Lines of Code: $LINES
- Git Commits: $COMMITS  
- Last Commit: $(git log -1 --pretty=format:"%h - %s (%cr)")

EOF

echo "✅ Reality check completed"
exit $((DOCKER_STATUS + BACKEND_STATUS))
```

#### **`scripts/pre-commit-reality.sh`**
```bash
#!/bin/bash
echo "🛡️ PRE-COMMIT REALITY CHECK"

# Run daily check first
./scripts/daily-check.sh
if [ $? -ne 0 ]; then
    echo "❌ Basic services not working. Fix before commit."
    exit 1
fi

# Check for aspirational language in commit message
COMMIT_MSG=$(git log -1 --pretty=format:"%s")
if [[ $COMMIT_MSG =~ (complete|finished|production-ready|enterprise) ]] && [[ ! $COMMIT_MSG =~ (partial|basic|start) ]]; then
    echo "⚠️  WARNING: Commit message claims completion. Verify with demo."
    read -p "Can you demo this functionality right now? (y/N): " -n 1 -r
    if [[ ! $REPL =~ ^[Yy]$ ]]; then
        echo "\n❌ Then don't claim it's complete. Revise commit message."
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
```

---

## 📚 **INSTRUCCIONES PARA DESARROLLADOR**

### **🎯 PARA KILO CODE - NUEVAS REGLAS**

```markdown
# INSTRUCCIONES CRÍTICAS - LEE ANTES DE CADA SESIÓN

## 🚨 ANTES DE EMPEZAR CUALQUIER TRABAJO
1. Ejecutar: `./scripts/daily-check.sh`
2. Si falla algo básico → ARREGLAR ANTES que nuevas features
3. Leer `docs/CURRENT_STATUS.md` para entender estado real

## 📝 DURANTE DESARROLLO
1. SOLO implementar funcionalidad específica y medible
2. Probar INMEDIATAMENTE cada cambio localmente
3. NO documentar hasta que funcione perfectamente

## ✅ ANTES DE CADA COMMIT  
1. Ejecutar: `./scripts/pre-commit-reality.sh`
2. Commit message debe describir QUÉ FUNCIONA, no qué planeas
3. Ejemplo: "feat: add login form (validates email)" NOT "complete authentication system"

## 📊 DESPUÉS DE CADA COMMIT
1. Ejecutar: `./scripts/update-status.sh` 
2. Verificar que `docs/CURRENT_STATUS.md` refleje realidad
3. Si algo está roto → fix inmediatamente

## 🎬 CADA VIERNES - DEMO TIME
1. Ejecutar: `./scripts/demo-prep.sh`
2. Preparar demo EN VIVO de funcionalidad nueva
3. Si no puedes hacer demo → feature NO está "completa"
4. Solo marcar como "completado" después de demo exitoso

## 🚫 PROHIBIDO ABSOLUTAMENTE
❌ Documentar features que no funcionan
❌ Usar palabras como "enterprise", "production-ready" sin evidencia
❌ Inventar métricas o fechas
❌ Marcar sprints como "completados" sin demos
❌ Editar manualmente archivos auto-generados
```

### **🔄 WORKFLOW EJEMPLO**

```bash
# CORRECTO ✅
./scripts/daily-check.sh           # Verificar estado
# [implementar login form]
curl -X POST localhost:7777/login  # Probar que funciona
./scripts/pre-commit-reality.sh    # Validar antes de commit
git commit -m "feat: add login form (validates email + password)"
./scripts/update-status.sh         # Actualizar estado

# INCORRECTO ❌  
git commit -m "feat: complete enterprise authentication system"
# [sin probar, sin validar, claim exagerado]
```

---

## 🎯 **SUCCESS METRICS**

### **PROYECTO SALUDABLE:**
- ✅ `daily-check.sh` pasa todos los días
- ✅ Demos semanales exitosos
- ✅ Documentación sincronizada < 24h
- ✅ Docker compose up funciona siempre

### **PROYECTO EN RIESGO:**
- ⚠️ `daily-check.sh` falla > 1 día
- ⚠️ Sin demos > 1 semana  
- ⚠️ Documentación desincronizada > 3 días
- ⚠️ Claims sin evidencia técnica

### **PROYECTO EN CRISIS:**
- 🚨 Servicios básicos rotos > 1 día
- 🚨 No hay código funcional para demos
- 🚨 Documentación no refleja realidad  
- 🚨 Métricas inventadas o editadas manualmente

---

## 📞 **ESCALATION PROTOCOL**

### **Si daily-check.sh falla:**
1. **Prioridad máxima**: Arreglar servicios básicos
2. No trabajar en features nuevas hasta que pase
3. Notificar inmediatamente si toma > 4 horas

### **Si no puedes hacer demo semanal:**
1. Rollback documentación aspiracional  
2. Re-priorizar a funcionalidad demostrable
3. Explicar gap entre expectativa y realidad

### **Si encuentras documentación incorrecta:**
1. STOP trabajo actual
2. Ejecutar auditoría completa
3. Corregir documentación antes de continuar

---

**🎯 OBJETIVO: "Zero Documentation Drift"**  
**📏 MEDIDA: "If you can't demo it, it doesn't exist"**  
**🛡️ PREVENCIÓN: "Validate reality every day"**