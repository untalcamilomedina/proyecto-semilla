# 🎯 INSTRUCCIONES CRÍTICAS PARA DESARROLLADOR
## "Zero Documentation Drift Protocol"

**LEER COMPLETO ANTES DE CADA SESIÓN DE DESARROLLO**

---

## 🚨 **REGLAS FUNDAMENTALES - NO NEGOCIABLES**

### **📊 FUENTE DE VERDAD**
```
1. Código funcionando = ÚNICA FUENTE DE VERDAD
2. Si no puedes hacer demo = NO EXISTE  
3. Si no pasa daily-check.sh = PRIORIDAD #1 arreglar
4. Documentación = Explicación del código, NUNCA promesas
```

### **❌ PROHIBIDO ABSOLUTAMENTE**
- Documentar features no implementadas
- Usar palabras como "complete", "enterprise", "production-ready" sin demo
- Inventar métricas o fechas  
- Marcar sprints/días como "completados" sin funcionalidad demostrable
- Editar manualmente archivos auto-generados

---

## 🔄 **WORKFLOW OBLIGATORIO**

### **🌅 INICIO DE CADA DÍA/SESIÓN**
```bash
# 1. SIEMPRE ejecutar antes de empezar
./scripts/daily-check.sh

# 2. Si falla algo → PRIORIDAD #1 arreglar
# NO trabajar en features nuevas hasta que pase

# 3. Leer estado actual
cat docs/CURRENT_STATUS.md
```

### **💻 DURANTE DESARROLLO**
```bash
# 1. Implementar UNA funcionalidad específica
# 2. Probar INMEDIATAMENTE en local
# 3. Verificar que funciona antes de continuar

# Ejemplo CORRECTO:
# - Implementar login form
# - curl -X POST localhost:7777/auth/login -d '{"email":"test@test.com"}'
# - Verificar que valida email y devuelve token
# - Solo entonces documentar: "login form validates email format"
```

### **📝 ANTES DE CADA COMMIT**
```bash
# 1. OBLIGATORIO - ejecutar pre-commit check
./scripts/pre-commit-reality.sh

# 2. Si te pregunta si puedes hacer demo → SÉ HONESTO
# 3. Commit message debe describir QUÉ FUNCIONA, no qué planeas

# EJEMPLOS:
# ✅ GOOD: "feat: add user login form (validates email + password)"
# ✅ GOOD: "fix: resolve SQLAlchemy async context in user endpoints"
# ✅ GOOD: "docs: update status - backend health check working"

# ❌ BAD: "feat: complete enterprise authentication system"
# ❌ BAD: "Sprint 8 Day 5 completed - all systems operational"
# ❌ BAD: "production-ready user management implemented"
```

### **📊 DESPUÉS DE CADA COMMIT**
```bash
# 1. Actualizar estado automáticamente
./scripts/update-status.sh  # (si existe)

# 2. Verificar que docs/CURRENT_STATUS.md refleja la realidad
# 3. Si algo se rompió → fix inmediatamente
```

---

## 🎬 **DEMO PROTOCOL - CADA VIERNES**

### **📋 PREPARACIÓN DEMO**
```bash
# 1. Ejecutar script de preparación
./scripts/demo-prep.sh  # (si existe)

# 2. Listar QUÉ puedes demostrar EN VIVO
# 3. Si no puedes hacer demo = feature NO está "completa"
```

### **🎯 REGLAS DEMO**
- **Solo demostrar funcionalidad que funciona SIN errores**
- **Demo debe ser en ambiente limpio (fresh docker-compose up)**  
- **Si algo falla durante demo = rollback documentación**
- **Marcar como "completado" SOLO después de demo exitoso**

---

## 📊 **EJEMPLOS PRÁCTICOS**

### **✅ CORRECTO - Desarrollo Incremental**
```bash
# Día 1
git commit -m "feat: add user model and database table"
# → Solo commitear cuando tabla se crea exitosamente

# Día 2  
git commit -m "feat: add user creation endpoint (validates email)"
# → Solo commitear cuando POST /users funciona con curl

# Día 3
git commit -m "feat: add user login endpoint (returns JWT token)"
# → Solo commitear cuando POST /auth/login devuelve token válido

# Viernes - DEMO
# "Puedo crear usuario, hacer login, recibir token"
# → Ahora SÍ puedes documentar: "Basic user authentication working"
```

### **❌ INCORRECTO - Aspirational Development**
```bash
# Día 1
git commit -m "feat: complete enterprise user management system"
# → Sin haber probado nada

# Documentación
"Sprint 8 Day 1 completed - Full authentication system operational"
# → Sin evidencia de funcionamiento

# Resultado: DOCUMENTATION DRIFT
```

---

## 🧪 **TESTING REQUIREMENTS**

### **📋 TESTING MÍNIMO ANTES DE COMMIT**
```bash
# 1. Servicios básicos funcionando
docker-compose up -d
curl http://localhost:7777/health  # Debe retornar 200

# 2. Feature específica funciona
curl -X POST localhost:7777/tu-endpoint -d '{test-data}'

# 3. Frontend compila (si aplicable)
cd frontend && npm run build
```

### **🔄 INTEGRATION TESTING**
```bash
# Cada viernes o antes de releases
# 1. Fresh environment
docker-compose down -v
docker-compose up -d --build

# 2. Smoke tests
curl http://localhost:7777/health
curl http://localhost:3001 # Frontend

# 3. Basic user flows
# Test real user scenarios end-to-end
```

---

## 🚨 **ESCALATION PROTOCOL**

### **🔴 Si daily-check.sh falla:**
1. **STOP** todo trabajo nuevo
2. **PRIORITY #1**: Arreglar servicios básicos
3. Si toma > 4 horas → Notificar y pedir ayuda

### **⚠️ Si no puedes hacer demo:**
1. **ROLLBACK** cualquier documentación aspiracional
2. **RE-PRIORIZAR** a funcionalidad demostrable
3. **DOCUMENTAR** gap entre expectativa y realidad

### **🚨 Si encuentras documentación incorrecta:**
1. **STOP** trabajo actual inmediatamente
2. **AUDIT** completo de documentación vs código
3. **CORREGIR** documentación antes de continuar

---

## 📈 **MÉTRICAS DE ÉXITO**

### **🟢 PROYECTO SALUDABLE:**
- `daily-check.sh` pasa todos los días
- Demos semanales exitosos  
- `docs/CURRENT_STATUS.md` actualizado automáticamente
- Commit messages descriptivos de funcionalidad real

### **🟡 PROYECTO EN RIESGO:**
- `daily-check.sh` falla > 1 día
- Sin demo exitoso > 1 semana
- Documentación desincronizada > 3 días  
- Claims aspiracionales en commits

### **🔴 PROYECTO EN CRISIS:**
- Servicios básicos rotos > 1 día
- No hay funcionalidad demostrable
- Documentación no refleja realidad
- Métricas inventadas o editadas manualmente

---

## 🎯 **TEMPLATES ÚTILES**

### **📝 Commit Message Templates**
```bash
# Features
feat: add [specific functionality] ([what it does])
# feat: add user login form (validates email format)

# Fixes  
fix: resolve [specific problem] in [component]
# fix: resolve SQLAlchemy async context in user routes

# Docs
docs: update [document] - [what changed]  
# docs: update API docs - add user endpoints

# Refactor
refactor: improve [component] ([why/how])
# refactor: improve error handling (consistent JSON responses)
```

### **📊 Status Update Template**
```markdown
## Daily Progress - [DATE]

### ✅ Working (Verified by testing)
- [Specific functionality with evidence]
- [Another working feature]

### 🔧 In Progress  
- [What you're currently implementing]
- [Expected completion: realistic timeframe]

### ❌ Blocked/Issues
- [Specific problems with error messages]
- [What you need to fix first]

### 📋 Next Priority
- [One specific, measurable task]
```

---

## 🎯 **OBJETIVOS CLAROS**

### **📍 PRIMARY GOAL:** 
"Zero Documentation Drift - Documentación siempre refleja código funcional"

### **📏 SUCCESS METRIC:**
"If you can't demo it live, it doesn't exist in documentation"

### **🛡️ PREVENTION STRATEGY:**
"Validate reality every day, demo functionality every week"

---

**🎯 RECUERDA: Tu trabajo es crear SOFTWARE FUNCIONAL, no documentación aspiracional.**

**📊 El éxito se mide por funcionalidad demostrable, no por documentos perfectos.**

**🚀 Un feature simple que funciona > Un sistema "enterprise" que no existe.**