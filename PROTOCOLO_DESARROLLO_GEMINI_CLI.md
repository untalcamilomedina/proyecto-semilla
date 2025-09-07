# 🚀 PROTOCOLO DE DESARROLLO - GEMINI CLI
## "Source of Truth Protocol - Zero Documentation Drift"

**Fecha de Creación**: 7 de septiembre de 2025  
**Versión**: 1.0  
**Desarrollador Objetivo**: Gemini CLI  
**Proyecto**: Proyecto Semilla - Primera plataforma SaaS Vibecoding-native

---

## 📁 **ESTRUCTURA DE DIRECTORIOS**

### **🔐 REPOSITORIO PRIVADO (Documentación y Planificación)**
```
/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla-privados/
├── indice/                           # 📊 Sistema de memoria y registro
│   ├── INDICE_SPRINTS_PROYECTO_SEMILLA.md    # Estado general del proyecto
│   ├── PLAN_SPRINTS_8_9_10.md               # Planificación actual
│   └── sprint*.md                           # Registro diario de progreso
├── PROTOCOLO_DESARROLLO_KILO_CODE.md        # ⚠️ Protocolo anterior (referencia)
└── (no sincronizar)/                        # Archivos que NO van al repo público
    └── website/                             # Website interno
```

### **🌍 REPOSITORIO PÚBLICO (Código y Implementación)**
```
/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla/
├── backend/                         # 🐍 FastAPI + PostgreSQL
│   ├── app/                        # Aplicación principal
│   ├── mcp/                        # MCP Protocol implementation
│   └── requirements.txt            # Dependencias Python
├── frontend/                       # ⚛️ Next.js + TypeScript (EN DESARROLLO)
├── scripts/                        # 🔧 Scripts de validación
│   ├── daily-check.sh             # ⭐ EJECUTAR DIARIAMENTE
│   └── pre-commit-reality.sh      # ⭐ EJECUTAR ANTES DE COMMITS
├── docs/                           # 📚 Documentación auto-generada
│   └── CURRENT_STATUS.md          # ⭐ Estado real del proyecto
├── docker-compose.yml              # 🐳 Configuración Docker
├── PROTOCOLO_SOURCE_OF_TRUTH.md    # 📋 Reglas fundamentales
├── INSTRUCCIONES_DESARROLLADOR.md  # 📖 Workflow obligatorio
└── MENSAJE_PARA_KILO_CODE.md      # 💌 Contexto del protocolo
```

---

## 🎯 **WORKFLOW OBLIGATORIO - GEMINI CLI**

### **🌅 INICIO DE CADA SESIÓN DE DESARROLLO**

#### **1. LECTURA OBLIGATORIA (Primera vez)**
```bash
# Leer protocolo completo
cat /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla/PROTOCOLO_SOURCE_OF_TRUTH.md

# Leer instrucciones de desarrollo
cat /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla/INSTRUCCIONES_DESARROLLADOR.md

# Revisar contexto histórico si es necesario
cat /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla-privados/PROTOCOLO_DESARROLLO_KILO_CODE.md
```

#### **2. VALIDACIÓN DIARIA OBLIGATORIA**
```bash
# Cambiar al directorio del proyecto público
cd /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla

# CRÍTICO: Ejecutar ANTES de cualquier trabajo
./scripts/daily-check.sh

# Si el script falla (exit code != 0):
# → PRIORITY #1: Arreglar servicios básicos
# → NO trabajar en features nuevas hasta que pase
```

#### **3. REVISAR ESTADO ACTUAL**
```bash
# Leer estado real del proyecto (auto-generado)
cat docs/CURRENT_STATUS.md

# Revisar planificación (repo privado)
cat /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla-privados/indice/PLAN_SPRINTS_8_9_10.md

# Verificar último progreso documentado
ls /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla-privados/indice/sprint*.md | tail -3
```

### **💻 DURANTE EL DESARROLLO**

#### **4. REGLAS DE IMPLEMENTACIÓN**
```bash
# ✅ CORRECTO: Desarrollo incremental y específico
# 1. Implementar UNA funcionalidad específica
# 2. Probar INMEDIATAMENTE en local
# 3. Verificar que funciona antes de continuar

# Ejemplo workflow:
# - git checkout -b feature/user-login-form
# - [implementar login form]
# - curl -X POST localhost:7777/auth/login -d '{"email":"test@test.com", "password":"test123"}'
# - [verificar respuesta correcta]
# - git add . && ./scripts/pre-commit-reality.sh
# - git commit -m "feat: add user login form (validates email + password)"
```

#### **5. TESTING REQUIREMENTS**
```bash
# MÍNIMO antes de cada commit:

# 1. Servicios básicos funcionando
docker-compose up -d
curl -f http://localhost:7777/health  # Debe retornar 200 OK

# 2. Feature específica funciona
curl -X POST localhost:7777/tu-nuevo-endpoint -d '{test-data}'

# 3. Frontend compila (si aplicable)
cd frontend && npm run build

# 4. Daily check pasa
./scripts/daily-check.sh  # Must return exit code 0
```

### **📝 ANTES DE CADA COMMIT**

#### **6. PRE-COMMIT VALIDATION**
```bash
# OBLIGATORIO - ejecutar antes de cada commit
./scripts/pre-commit-reality.sh

# El script validará:
# - Servicios básicos funcionando
# - Commit message realista (no aspiracional)
# - Changes match claimed functionality
# - Basic functionality not broken
```

#### **7. COMMIT MESSAGE STANDARDS**
```bash
# ✅ BUENOS EJEMPLOS:
git commit -m "feat: add user login endpoint (validates email, returns JWT)"
git commit -m "fix: resolve SQLAlchemy async context in user routes"
git commit -m "docs: update API documentation for working endpoints"
git commit -m "refactor: improve error handling (consistent JSON responses)"

# ❌ MALOS EJEMPLOS (Script los bloqueará):
git commit -m "feat: complete enterprise authentication system"
git commit -m "Sprint 8 Day 5 completed - all features operational"
git commit -m "production-ready user management implemented"
git commit -m "add comprehensive security hardening"
```

### **📊 DESPUÉS DE CADA COMMIT**

#### **8. STATUS UPDATE**
```bash
# Verificar que el estado se actualizó correctamente
cat docs/CURRENT_STATUS.md

# Si algo se rompió → fix inmediatamente
./scripts/daily-check.sh
```

---

## 📋 **REGISTRO DE PROGRESO**

### **🔄 DOCUMENTACIÓN DUAL**

#### **Repo Público (Código Real)**
```bash
# Estado técnico real (auto-generado)
/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla/docs/CURRENT_STATUS.md

# Commits como fuente de verdad
cd /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla
git log --oneline -10
```

#### **Repo Privado (Planificación y Registro)**
```bash
# Crear archivo de progreso diario
cat > /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla-privados/indice/sprint9-gemini-day1.md << 'EOF'
# 📅 SPRINT 9 DÍA 1 - GEMINI CLI
## Fecha: $(date +"%d de %B de %Y")

## 🎯 Objetivos del Día
- [ ] [OBJETIVO_ESPECÍFICO_MEDIBLE]
- [ ] [OBJETIVO_ESPECÍFICO_MEDIBLE]

## 🔧 Trabajo Realizado

### [HORA] - [TAREA_ESPECÍFICA]
**Tiempo**: [DURACIÓN]
**Archivos**: [ARCHIVOS_MODIFICADOS]
**Descripción**: [QUÉ_FUNCIONA_REALMENTE]
**Resultado**: [✅ EXITOSO | ⚠️ PARCIAL | ❌ FALLIDO] - [EVIDENCIA]

## 📊 Métricas Reales
- Líneas de código: [AUTO_CALCULADO_DE_CURRENT_STATUS]
- Tests añadidos: [NÚMERO_REAL_DE_TESTS]
- Bugs resueltos: [ESPECÍFICOS_CON_DESCRIPCIÓN]
- Features completadas: [SOLO_LAS_QUE_PUEDES_DEMOSTRAR]

## 🎯 Próximos Pasos
1. [TAREA_ESPECÍFICA_CON_ETA_REALISTA]
2. [TAREA_ESPECÍFICA_CON_ETA_REALISTA]

EOF
```

---

## 🎬 **DEMO PROTOCOL**

### **📅 WEEKLY DEMOS (Cada Viernes)**

#### **Preparación Demo**
```bash
# 1. Verificar que todo funciona
cd /Users/untalcamilomedina/Documents/GitHub/proyecto-semilla
./scripts/daily-check.sh

# 2. Fresh environment test
docker-compose down -v
docker-compose up -d --build

# 3. Listar funcionalidad demostrable
echo "## Funcionalidad Demostrable $(date)" > DEMO_CHECKLIST.md
echo "- [ ] [FEATURE] - [EVIDENCIA: curl command o URL]" >> DEMO_CHECKLIST.md
```

#### **Demo Requirements**
- **Solo demostrar funcionalidad que funciona SIN errores**
- **Demo en ambiente limpio (fresh docker-compose up)**
- **Si algo falla durante demo = rollback documentación aspiracional**
- **Marcar como "completado" SOLO después de demo exitoso**

---

## 🚨 **REGLAS FUNDAMENTALES**

### **❌ PROHIBIDO ABSOLUTAMENTE**
1. Documentar features no implementadas
2. Usar palabras como "complete", "enterprise", "production-ready" sin demo
3. Inventar métricas, fechas o estadísticas
4. Marcar sprints/días como "completados" sin funcionalidad demostrable
5. Editar manualmente archivos auto-generados (CURRENT_STATUS.md)
6. Commitear código que rompe servicios básicos
7. Hacer claims aspiracionales en commit messages

### **✅ OBLIGATORIO**
1. Ejecutar `./scripts/daily-check.sh` al inicio de cada sesión
2. Solo commitear funcionalidad que puedas demostrar EN VIVO
3. Probar cada cambio inmediatamente después de implementar
4. Mantener servicios básicos siempre funcionando
5. Commit messages descriptivos de funcionalidad real
6. Documentar en repo privado progreso real vs planificado
7. Demo semanal de funcionalidad nueva

---

## 🔧 **TROUBLESHOOTING COMÚN**

### **Si `daily-check.sh` falla:**
```bash
# Docker issues
docker-compose down -v
docker-compose up -d --build

# Frontend compilation issues  
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build

# Backend issues
cd backend
pip install -r requirements.txt
python -m pytest --tb=short (si hay tests)

# Re-test
./scripts/daily-check.sh
```

### **Si `pre-commit-reality.sh` bloquea commit:**
```bash
# Analizar por qué fue bloqueado
# 1. ¿Servicios básicos fallan? → Arreglar primero
# 2. ¿Mensaje aspiracional? → Reescribir más específico
# 3. ¿No puedes hacer demo? → No commitear como "completado"

# Ejemplo de corrección:
git commit --amend -m "feat: add login form validation (checks email format)"
# En lugar de: "feat: complete authentication system"
```

---

## 📊 **MÉTRICAS Y MONITOREO**

### **🟢 PROYECTO SALUDABLE**
- ✅ `daily-check.sh` pasa todos los días
- ✅ Demos semanales exitosos  
- ✅ `CURRENT_STATUS.md` actualizado automáticamente
- ✅ Commit messages descriptivos de funcionalidad real
- ✅ Docker compose up funciona siempre
- ✅ No discrepancias entre repo público y privado

### **🟡 PROYECTO EN RIESGO**
- ⚠️ `daily-check.sh` falla > 1 día
- ⚠️ Sin demo exitoso > 1 semana
- ⚠️ Servicios básicos inestables
- ⚠️ Commits aspiracionales frequent
- ⚠️ Documentación desincronizada > 3 días

### **🔴 PROYECTO EN CRISIS**
- 🚨 Servicios básicos rotos > 1 día
- 🚨 No hay funcionalidad demostrable
- 🚨 Multiple failed daily checks
- 🚨 Documentación privada/pública contradictoria
- 🚨 Claims no respaldados por código

---

## 🎯 **OBJETIVOS ACTUALES (Basado en Planificación Real)**

### **SPRINT 9: OAUTH FOUNDATION**
**Ubicación**: `/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla-privados/indice/PLAN_SPRINTS_8_9_10.md`

#### **Prioridades Técnicas:**
1. **Arreglar issues básicos** (Docker + Frontend compilation)
2. **Implementar OAuth 2.0 con Google** (flow completo)
3. **User registration automático** con profile sync
4. **Account linking** con usuarios existentes
5. **Multi-tenant OAuth apps** configuration

#### **Definition of Done:**
- [ ] OAuth flow funciona end-to-end
- [ ] Demo live: "Login con Google" exitoso
- [ ] Usuario se crea automáticamente
- [ ] Profile sync (avatar, email, name) working
- [ ] Integration tests passing
- [ ] Docker setup funcional completo

---

## 📚 **RESOURCES Y REFERENCIAS**

### **Documentos Clave**
- `PROTOCOLO_SOURCE_OF_TRUTH.md` - Reglas fundamentales
- `INSTRUCCIONES_DESARROLLADOR.md` - Workflow detallado  
- `docs/CURRENT_STATUS.md` - Estado técnico real
- Repo privado: `indice/PLAN_SPRINTS_8_9_10.md` - Roadmap

### **Scripts Críticos**
- `./scripts/daily-check.sh` - Validación diaria obligatoria
- `./scripts/pre-commit-reality.sh` - Quality gate commits

### **Testing Commands**
```bash
# Health checks básicos
curl -f http://localhost:7777/health
curl -f http://localhost:3001

# Docker validation
docker-compose ps
docker-compose logs backend | tail -20
docker-compose logs frontend | tail -20

# Code metrics
find backend -name "*.py" | xargs wc -l
find frontend -name "*.ts*" | xargs wc -l
```

---

## 🔄 **ESCALATION PROTOCOL**

### **Si problemas técnicos > 4 horas:**
1. Documentar issue específico en repo privado
2. Intentar rollback a último commit funcional
3. Focus en daily-check.sh passing antes que features

### **Si daily-check.sh falla consistentemente:**
1. STOP todo desarrollo nuevo
2. PRIORITY #1: Estabilizar servicios básicos
3. No claims de progreso hasta resolver

### **Si encuentras documentación incorrecta:**
1. AUDIT completo repo privado vs público
2. Corregir discrepancias inmediatamente  
3. Documentar causas para prevenir repetición

---

## 🏆 **SUCCESS METRICS**

### **Daily Success:**
- ✅ `daily-check.sh` passes
- ✅ Commits with working functionality
- ✅ Progress documented realistically

### **Weekly Success:**
- ✅ Live demo of new features
- ✅ All basic services stable
- ✅ Repo privado/público synchronized

### **Sprint Success:**
- ✅ Definition of Done met with evidence
- ✅ Functionality demostrable end-to-end
- ✅ No broken functionality regression

---

**🎯 OBJETIVO PRINCIPAL: "Zero Documentation Drift"**  
**📏 SUCCESS METRIC: "If you can't demo it live, it doesn't exist"**  
**🛡️ PREVENTION: "Daily validation + Weekly demos + Reality-first commits"**

---

**🤖 GEMINI CLI: Tu trabajo es crear SOFTWARE FUNCIONAL, no documentación aspiracional.**  
**📊 El éxito se mide por funcionalidad demostrable, no por documentos perfectos.**  
**🚀 Un feature simple que funciona > Un sistema "enterprise" que no existe.**