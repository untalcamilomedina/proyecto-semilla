# 🤝 Guía de Contribución - Proyecto Semilla

[![English](https://img.shields.io/badge/Language-English-blue.svg)](#english-version)
[![Español](https://img.shields.io/badge/Idioma-Español-green.svg)](#versión-en-español)

---

## 🇪🇸 Versión en Español

¡Gracias por tu interés en contribuir a **Proyecto Semilla**! Esta guía te ayudará a hacer contribuciones efectivas al proyecto.

### 📋 Tabla de Contenidos

1. [Cómo Contribuir](#-cómo-contribuir)
2. [Configuración del Entorno](#-configuración-del-entorno)
3. [Estándares de Código](#-estándares-de-código)
4. [Proceso de Desarrollo](#-proceso-de-desarrollo)
5. [Tipos de Contribución](#-tipos-de-contribución)
6. [Revisión de Código](#-revisión-de-código)
7. [Comunidad](#-comunidad)

### 🌟 Cómo Contribuir

Hay muchas formas de contribuir al proyecto, desde reportar bugs hasta implementar nuevas características:

#### 🐛 Reportar Bugs
- Revisa los [issues existentes](../../issues) para evitar duplicados
- Usa el [template de bug report](../../issues/new?template=bug_report.md)
- Incluye información detallada para reproducir el problema
- Adjunta screenshots, logs o cualquier información relevante

#### ✨ Sugerir Características
- Abre una [discussion](../../discussions/new?category=ideas) para discutir la idea
- Explica claramente el caso de uso y los beneficios
- Espera feedback de la comunidad antes de implementar

#### 💻 Contribuir con Código
- Fork el repositorio
- Crea una rama para tu feature: `git checkout -b feat/nueva-caracteristica`
- Implementa tu código siguiendo los estándares
- Escribe tests para tu código
- Haz commit con mensajes descriptivos
- Abre un Pull Request

#### 📚 Mejorar Documentación
- Corrige errores tipográficos
- Mejora explicaciones existentes
- Añade ejemplos y casos de uso
- Traduce contenido al inglés/español

### ⚙️ Configuración del Entorno

#### Prerrequisitos
```bash
# Herramientas requeridas
- Git
- Docker y Docker Compose
- Python 3.11+
- Node.js 18+
- VS Code (recomendado)
```

#### 1. Fork y Clonar
```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/proyecto-semilla.git
cd proyecto-semilla

# Añadir remote upstream
git remote add upstream https://github.com/proyecto-semilla/proyecto-semilla.git
```

#### 2. Instalar Dependencias de Desarrollo
```bash
# Instalar pre-commit hooks
pip install pre-commit
pre-commit install

# Instalar dependencias Python
pip install -r requirements-dev.txt

# Instalar dependencias Node.js (para frontend)
cd frontend
npm install
cd ..
```

#### 3. Configurar Entorno Local
```bash
# Copiar variables de entorno
cp .env.example .env

# Levantar servicios con Docker
docker-compose up -d db redis

# Ejecutar migraciones
alembic upgrade head
```

### 📝 Estándares de Código

#### Principios Generales
- **Idioma del Código**: Inglés (variables, funciones, comentarios)
- **Documentación**: Español primario + Inglés secundario
- **Legibilidad**: Código autodocumentado y bien estructurado
- **Testing**: Cobertura mínima del 80%

#### Python (Backend)
```python
# ✅ Correcto - Inglés para código
class UserService:
    """Service for managing user operations."""
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user in the system."""
        pass

# ❌ Incorrecto - Español para código  
class ServicioUsuario:
    def crear_usuario(self, datos_usuario):
        pass
```

**Herramientas de Calidad**:
- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`
- **Type Checking**: `mypy .`
- **Testing**: `pytest`

#### TypeScript (Frontend)
```typescript
// ✅ Correcto - Inglés para código
interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}

const fetchUserProfile = async (userId: string): Promise<UserProfile> => {
  // Implementation
};

// ❌ Incorrecto - Español para código
interface PerfilUsuario {
  id: string;
  correo: string;
}
```

**Herramientas de Calidad**:
- **Linting**: `npm run lint`
- **Formatting**: `npm run format`
- **Type Checking**: `npm run type-check`
- **Testing**: `npm run test`

### 🔄 Proceso de Desarrollo

#### 1. Conventional Commits
Utilizamos [Conventional Commits](https://www.conventionalcommits.org/) para mensajes consistentes:

```bash
# Estructura
<tipo>[scope opcional]: <descripción>

# Ejemplos
feat: add user authentication system
fix(api): resolve permission validation bug
docs: update installation guide
chore: update dependencies
```

**Tipos Principales**:
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato de código
- `refactor`: Refactorización
- `test`: Pruebas
- `chore`: Mantenimiento

#### 2. Flujo de Trabajo (GitHub Flow)
```bash
# 1. Sincronizar con upstream
git checkout main
git pull upstream main

# 2. Crear rama de feature
git checkout -b feat/user-management

# 3. Desarrollo iterativo
git add .
git commit -m "feat: add user creation endpoint"

# 4. Mantener actualizado
git pull upstream main
git rebase main  # O merge si prefieres

# 5. Push y PR
git push origin feat/user-management
# Crear PR en GitHub
```

#### 3. Estructura de Ramas
- `main`: Rama estable, siempre deployable
- `feat/nombre-caracteristica`: Nuevas características
- `fix/descripcion-bug`: Corrección de bugs
- `docs/descripcion`: Documentación
- `hotfix/descripcion`: Fixes críticos

### 🎯 Tipos de Contribución

#### 🚀 Características Nuevas
1. **Discusión**: Abre issue o discussion
2. **Diseño**: Define arquitectura y API
3. **Implementación**: Código + tests + docs
4. **Review**: Revisión de código y feedback
5. **Merge**: Integración a main

#### 🐛 Corrección de Bugs
1. **Reproducir**: Confirmar el bug
2. **Test**: Escribir test que falle
3. **Fix**: Implementar solución
4. **Verificar**: Test pasa y no se rompe nada
5. **Documentar**: Actualizar CHANGELOG

#### 📚 Documentación
- **README**: Información general y setup
- **API Docs**: Documentación de endpoints
- **Guides**: Tutoriales paso a paso
- **Architecture**: Documentación técnica

#### 🧪 Testing
- **Unit Tests**: Funciones y métodos individuales
- **Integration Tests**: Flujos completos
- **E2E Tests**: Casos de uso reales
- **Performance Tests**: Benchmarks y carga

### 👀 Revisión de Código

#### Checklist del Autor
Antes de abrir un PR, verifica:

- ✅ El código sigue los estándares del proyecto
- ✅ Todos los tests pasan (`pytest` y `npm test`)
- ✅ Cobertura de tests cumple el mínimo (80%)
- ✅ Documentación actualizada si es necesario
- ✅ Commit messages siguen Conventional Commits
- ✅ No hay secretos o información sensible
- ✅ PR tiene descripción clara y detallada

#### Checklist del Reviewer
Como reviewer, evalúa:

- ✅ **Funcionalidad**: ¿Hace lo que dice que hace?
- ✅ **Diseño**: ¿Sigue los patrones del proyecto?
- ✅ **Performance**: ¿Hay impacto en rendimiento?
- ✅ **Security**: ¿Introduce vulnerabilidades?
- ✅ **Tests**: ¿Cobertura y calidad adecuada?
- ✅ **Documentation**: ¿Está bien documentado?

#### Feedback Constructivo
```markdown
# ✅ Bueno - Específico y constructivo
Sugerencia: En línea 45, considera usar `asyncio.gather()` 
para las llamadas concurrentes. Esto mejorará el performance.

# ❌ Malo - Vago y poco útil
Este código no está bien.
```

### 🌐 Comunidad

#### Canales de Comunicación
- 💬 **Discord**: [discord.gg/proyecto-semilla](https://discord.gg/proyecto-semilla)
- 🐦 **Twitter**: [@ProyectoSemilla](https://twitter.com/ProyectoSemilla)
- 📧 **Email**: contributors@proyecto-semilla.com

#### Código de Conducta
Este proyecto adopta el [Contributor Covenant](./CODE_OF_CONDUCT.md). Al participar, aceptas seguir este código.

#### Reconocimientos
Todos los contributors son reconocidos en:
- README.md del proyecto
- Archivo AUTHORS
- Release notes
- Wall of Fame en Discord

---

## 🇺🇸 English Version

Thank you for your interest in contributing to **Proyecto Semilla**! This guide will help you make effective contributions to the project.

### 📋 Table of Contents

1. [How to Contribute](#-how-to-contribute-en)
2. [Environment Setup](#-environment-setup-en)
3. [Code Standards](#-code-standards-en)
4. [Development Process](#-development-process-en)
5. [Contribution Types](#-contribution-types-en)
6. [Code Review](#-code-review-en)
7. [Community](#-community-en)

### 🌟 How to Contribute {#how-to-contribute-en}

There are many ways to contribute to the project, from reporting bugs to implementing new features:

#### 🐛 Report Bugs
- Check [existing issues](../../issues) to avoid duplicates
- Use the [bug report template](../../issues/new?template=bug_report.md)
- Include detailed information to reproduce the problem
- Attach screenshots, logs, or any relevant information

#### ✨ Suggest Features
- Open a [discussion](../../discussions/new?category=ideas) to discuss the idea
- Clearly explain the use case and benefits
- Wait for community feedback before implementing

#### 💻 Contribute Code
- Fork the repository
- Create a branch for your feature: `git checkout -b feat/new-feature`
- Implement your code following standards
- Write tests for your code
- Commit with descriptive messages
- Open a Pull Request

#### 📚 Improve Documentation
- Fix typos
- Improve existing explanations
- Add examples and use cases
- Translate content to English/Spanish

### ⚙️ Environment Setup {#environment-setup-en}

#### Prerequisites
```bash
# Required tools
- Git
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- VS Code (recommended)
```

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/proyecto-semilla.git
cd proyecto-semilla

# Add upstream remote
git remote add upstream https://github.com/proyecto-semilla/proyecto-semilla.git
```

#### 2. Install Development Dependencies
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install Python dependencies
pip install -r requirements-dev.txt

# Install Node.js dependencies (for frontend)
cd frontend
npm install
cd ..
```

#### 3. Setup Local Environment
```bash
# Copy environment variables
cp .env.example .env

# Start services with Docker
docker-compose up -d db redis

# Run migrations
alembic upgrade head
```

### 📝 Code Standards {#code-standards-en}

#### General Principles
- **Code Language**: English (variables, functions, comments)
- **Documentation**: Spanish primary + English secondary
- **Readability**: Self-documented and well-structured code
- **Testing**: Minimum 80% coverage

#### Python (Backend)
```python
# ✅ Correct - English for code
class UserService:
    """Service for managing user operations."""
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user in the system."""
        pass

# ❌ Incorrect - Spanish for code  
class ServicioUsuario:
    def crear_usuario(self, datos_usuario):
        pass
```

**Quality Tools**:
- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`
- **Type Checking**: `mypy .`
- **Testing**: `pytest`

#### TypeScript (Frontend)
```typescript
// ✅ Correct - English for code
interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}

const fetchUserProfile = async (userId: string): Promise<UserProfile> => {
  // Implementation
};
```

**Quality Tools**:
- **Linting**: `npm run lint`
- **Formatting**: `npm run format`
- **Type Checking**: `npm run type-check`
- **Testing**: `npm run test`

### 🔄 Development Process {#development-process-en}

#### 1. Conventional Commits
We use [Conventional Commits](https://www.conventionalcommits.org/) for consistent messages:

```bash
# Structure
<type>[optional scope]: <description>

# Examples
feat: add user authentication system
fix(api): resolve permission validation bug
docs: update installation guide
chore: update dependencies
```

#### 2. Workflow (GitHub Flow)
```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feat/user-management

# 3. Iterative development
git add .
git commit -m "feat: add user creation endpoint"

# 4. Keep updated
git pull upstream main
git rebase main

# 5. Push and PR
git push origin feat/user-management
# Create PR on GitHub
```

### 🎯 Contribution Types {#contribution-types-en}

#### 🚀 New Features
1. **Discussion**: Open issue or discussion
2. **Design**: Define architecture and API
3. **Implementation**: Code + tests + docs
4. **Review**: Code review and feedback
5. **Merge**: Integration to main

#### 🐛 Bug Fixes
1. **Reproduce**: Confirm the bug
2. **Test**: Write failing test
3. **Fix**: Implement solution
4. **Verify**: Test passes and nothing breaks
5. **Document**: Update CHANGELOG

### 👀 Code Review {#code-review-en}

#### Author Checklist
Before opening a PR, verify:

- ✅ Code follows project standards
- ✅ All tests pass (`pytest` and `npm test`)
- ✅ Test coverage meets minimum (80%)
- ✅ Documentation updated if necessary
- ✅ Commit messages follow Conventional Commits
- ✅ No secrets or sensitive information
- ✅ PR has clear and detailed description

### 🌐 Community {#community-en}

#### Communication Channels
- 💬 **Discord**: [discord.gg/proyecto-semilla](https://discord.gg/proyecto-semilla)
- 🐦 **Twitter**: [@ProyectoSemilla](https://twitter.com/ProyectoSemilla)
- 📧 **Email**: contributors@proyecto-semilla.com

#### Code of Conduct
This project adopts the [Contributor Covenant](./CODE_OF_CONDUCT.md). By participating, you agree to follow this code.

---

## 🙏 Agradecimientos / Acknowledgments

¡Gracias a todos los que han contribuido y continuarán contribuyendo a **Proyecto Semilla**! / Thanks to everyone who has contributed and will continue contributing to **Proyecto Semilla**!

### 🌟 Top Contributors
<!-- This will be automatically updated -->
- [Contributor List](../../graphs/contributors)

---

*¿Tienes preguntas sobre cómo contribuir? / Have questions about contributing?*  
*¡Únete a nuestro Discord o abre un issue! / Join our Discord or open an issue!*