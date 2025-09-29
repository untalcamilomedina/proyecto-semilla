#!/bin/bash

# 🚀 Vibecoding Setup Verification Script
# Versión: 1.0.0
# Fecha: 2025-09-04
# Propósito: Verificar que la configuración del proyecto esté completa y funcional

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}🔍 VIBECODING SETUP VERIFICATION${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_section() {
    echo -e "${YELLOW}📋 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_file_exists() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        print_success "$description encontrado: $file"
        return 0
    else
        print_error "$description NO encontrado: $file"
        return 1
    fi
}

check_directory_exists() {
    local dir=$1
    local description=$2

    if [ -d "$dir" ]; then
        print_success "$description encontrado: $dir"
        return 0
    else
        print_error "$description NO encontrado: $dir"
        return 1
    fi
}

check_dependency() {
    local package=$1
    local description=$2

    if npm list "$package" >/dev/null 2>&1; then
        print_success "$description instalado"
        return 0
    else
        print_error "$description NO instalado: $package"
        return 1
    fi
}

check_file_content() {
    local file=$1
    local pattern=$2
    local description=$3

    if [ -f "$file" ] && grep -q "$pattern" "$file"; then
        print_success "$description correcto en $file"
        return 0
    else
        print_error "$description INCORRECTO en $file"
        return 1
    fi
}

# Main verification process
main() {
    print_header

    local errors=0
    local warnings=0

    # 1. Verificar estructura de archivos
    print_section "VERIFICANDO ESTRUCTURA DE ARCHIVOS"

    # Archivos de configuración críticos
    check_file_exists "package.json" "Package.json" || ((errors++))
    check_file_exists "tailwind.config.js" "Configuración Tailwind" || ((errors++))
    check_file_exists "postcss.config.js" "Configuración PostCSS" || ((errors++))
    check_file_exists "vite.config.ts" "Configuración Vite" || ((errors++))
    check_file_exists "tsconfig.json" "Configuración TypeScript" || ((errors++))
    check_file_exists "index.html" "HTML principal" || ((errors++))

    # Directorios importantes
    check_directory_exists "src" "Directorio src" || ((errors++))
    check_directory_exists "src/components" "Componentes" || ((errors++))
    check_directory_exists "src/styles" "Estilos" || ((errors++))

    echo ""

    # 2. Verificar dependencias críticas
    print_section "VERIFICANDO DEPENDENCIAS"

    check_dependency "react" "React" || ((errors++))
    check_dependency "react-dom" "React DOM" || ((errors++))
    check_dependency "typescript" "TypeScript" || ((errors++))
    check_dependency "tailwindcss" "Tailwind CSS" || ((errors++))
    check_dependency "autoprefixer" "Autoprefixer" || ((errors++))
    check_dependency "postcss" "PostCSS" || ((errors++))
    check_dependency "vite" "Vite" || ((errors++))
    check_dependency "@vitejs/plugin-react" "Vite React Plugin" || ((errors++))

    echo ""

    # 3. Verificar contenido de archivos críticos
    print_section "VERIFICANDO CONTENIDO DE ARCHIVOS"

    # Verificar package.json
    check_file_content "package.json" '"type": "module"' "Type module en package.json" || ((warnings++))
    check_file_content "package.json" '"dev": "vite"' "Script dev en package.json" || ((warnings++))

    # Verificar estilos principales
    check_file_content "src/styles/index.css" "@tailwind base" "Directiva @tailwind base" || ((errors++))
    check_file_content "src/styles/index.css" "@tailwind components" "Directiva @tailwind components" || ((errors++))
    check_file_content "src/styles/index.css" "@tailwind utilities" "Directiva @tailwind utilities" || ((errors++))

    # Verificar configuración Tailwind
    check_file_content "tailwind.config.js" "content:" "Configuración content en Tailwind" || ((errors++))
    check_file_content "tailwind.config.js" "theme:" "Configuración theme en Tailwind" || ((warnings++))

    # Verificar PostCSS
    check_file_content "postcss.config.js" "tailwindcss" "Plugin tailwindcss en PostCSS" || ((errors++))
    check_file_content "postcss.config.js" "autoprefixer" "Plugin autoprefixer en PostCSS" || ((errors++))

    echo ""

    # 4. Verificar build process
    print_section "VERIFICANDO BUILD PROCESS"

    echo "🏗️  Ejecutando build de prueba..."
    if npm run build >/dev/null 2>&1; then
        print_success "Build exitoso"
    else
        print_error "Build FALLÓ"
        ((errors++))
    fi

    echo ""

    # 5. Verificar componentes críticos
    print_section "VERIFICANDO COMPONENTES"

    check_file_exists "src/main.tsx" "Entry point main.tsx" || ((errors++))
    check_file_exists "src/App.tsx" "Componente App.tsx" || ((errors++))
    check_file_exists "src/components/Dashboard.tsx" "Componente Dashboard" || ((warnings++))
    check_file_exists "src/components/TestStyles.tsx" "Componente TestStyles (diagnóstico)" || ((warnings++))

    echo ""

    # 6. Resultados finales
    echo "=================================================="
    echo "📊 RESULTADOS DE LA VERIFICACIÓN"
    echo "=================================================="

    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}🎉 ¡CONFIGURACIÓN COMPLETA Y FUNCIONAL!${NC}"
        echo ""
        echo "✅ Todos los archivos críticos están presentes"
        echo "✅ Todas las dependencias están instaladas"
        echo "✅ Build process funciona correctamente"
        echo "✅ Configuración de Tailwind es correcta"
        echo ""
        echo "🚀 El proyecto está listo para desarrollo"
        echo "💡 Ejecuta: npm run dev"
        echo "🌐 Abre: http://localhost:3002/"
        exit 0
    else
        echo -e "${RED}❌ CONFIGURACIÓN INCOMPLETA${NC}"
        echo ""
        echo "Errores críticos encontrados: $errors"
        if [ $warnings -gt 0 ]; then
            echo "Advertencias: $warnings"
        fi
        echo ""
        echo "🔧 Soluciones recomendadas:"
        echo "1. Verifica que todos los archivos de configuración existan"
        echo "2. Ejecuta: npm install"
        echo "3. Verifica las dependencias críticas"
        echo "4. Revisa el contenido de los archivos de configuración"
        echo ""
        echo "📖 Consulta POST_MORTEM_ANALYSIS.md para más detalles"
        exit 1
    fi
}

# Ejecutar verificación
main "$@"