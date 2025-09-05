#!/bin/bash

# Performance Testing Script for Proyecto Semilla
# Executes Artillery load tests and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_CONFIG="$PROJECT_ROOT/tests/performance/load-test.yml"
RESULTS_DIR="$PROJECT_ROOT/tests/performance/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create results directory
mkdir -p "$RESULTS_DIR"

echo -e "${BLUE}🚀 Iniciando Performance Tests - Proyecto Semilla${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if Artillery is installed
if ! command -v artillery &> /dev/null; then
    echo -e "${RED}❌ Artillery no está instalado${NC}"
    echo -e "${YELLOW}📦 Instala Artillery con: npm install -g artillery${NC}"
    exit 1
fi

# Check if server is running
echo -e "${YELLOW}🔍 Verificando que el servidor esté ejecutándose...${NC}"
if ! curl -s http://localhost:7777/health > /dev/null; then
    echo -e "${RED}❌ El servidor no está ejecutándose en http://localhost:7777${NC}"
    echo -e "${YELLOW}💡 Inicia el servidor con: python -m uvicorn app.main:app --host 0.0.0.0 --port 7777${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Servidor detectado en http://localhost:7777${NC}"

# Run warm-up test
echo -e "${YELLOW}🔥 Ejecutando warm-up test...${NC}"
artillery run --config "$TEST_CONFIG" --overrides '{"config":{"phases":[{"duration":30,"arrivalRate":2,"name":"Warm-up"}]}}' > /dev/null 2>&1
echo -e "${GREEN}✅ Warm-up completado${NC}"

# Run main performance test
echo -e "${YELLOW}📊 Ejecutando performance test principal...${NC}"
RESULTS_FILE="$RESULTS_DIR/performance_test_$TIMESTAMP.json"

artillery run "$TEST_CONFIG" \
    --output "$RESULTS_FILE" \
    --overrides '{"config":{"phases":[{"duration":60,"arrivalRate":10,"name":"Quick Test"}]}}'

# Generate HTML report
echo -e "${YELLOW}📈 Generando reporte HTML...${NC}"
HTML_REPORT="$RESULTS_DIR/performance_report_$TIMESTAMP.html"
artillery report "$RESULTS_FILE" --output "$HTML_REPORT"

# Parse results and show summary
echo -e "${BLUE}📊 RESULTADOS DEL PERFORMANCE TEST${NC}"
echo -e "${BLUE}===================================${NC}"

# Extract key metrics from JSON results
if command -v jq &> /dev/null; then
    echo -e "${GREEN}✅ Métricas principales:${NC}"

    # Response time metrics
    AVG_RESPONSE_TIME=$(jq -r '.aggregate.summary."http.response_time".mean' "$RESULTS_FILE" 2>/dev/null || echo "N/A")
    P95_RESPONSE_TIME=$(jq -r '.aggregate.summary."http.response_time".p95' "$RESULTS_FILE" 2>/dev/null || echo "N/A")
    P99_RESPONSE_TIME=$(jq -r '.aggregate.summary."http.response_time".p99' "$RESULTS_FILE" 2>/dev/null || echo "N/A")

    # Request metrics
    TOTAL_REQUESTS=$(jq -r '.aggregate.counters."http.requests"' "$RESULTS_FILE" 2>/dev/null || echo "N/A")
    REQUESTS_PER_SECOND=$(jq -r '.aggregate.rates."http.requests"' "$RESULTS_FILE" 2>/dev/null || echo "N/A")

    # Error metrics
    ERROR_RATE=$(jq -r '.aggregate.counters."errors.ETIMEDOUT" // 0' "$RESULTS_FILE" 2>/dev/null || echo "0")

    echo -e "⏱️  Response Time - Avg: ${GREEN}${AVG_RESPONSE_TIME}ms${NC}"
    echo -e "📊 Response Time - P95: ${GREEN}${P95_RESPONSE_TIME}ms${NC}"
    echo -e "🎯 Response Time - P99: ${GREEN}${P99_RESPONSE_TIME}ms${NC}"
    echo -e "📈 Total Requests: ${GREEN}${TOTAL_REQUESTS}${NC}"
    echo -e "⚡ Requests/sec: ${GREEN}${REQUESTS_PER_SECOND}${NC}"
    echo -e "❌ Error Rate: ${RED}${ERROR_RATE}${NC}"

    # Performance assessment
    echo -e "${BLUE}🎯 EVALUACIÓN DE PERFORMANCE${NC}"
    if (( $(echo "$P95_RESPONSE_TIME < 200" | bc -l 2>/dev/null || echo "false") )); then
        echo -e "${GREEN}✅ EXCELENTE: P95 < 200ms${NC}"
    elif (( $(echo "$P95_RESPONSE_TIME < 500" | bc -l 2>/dev/null || echo "false") )); then
        echo -e "${YELLOW}⚠️  BUENO: P95 < 500ms${NC}"
    else
        echo -e "${RED}❌ REQUIERE OPTIMIZACIÓN: P95 > 500ms${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  jq no está instalado - instala para ver métricas detalladas${NC}"
    echo -e "${YELLOW}📊 Revisa el archivo JSON: $RESULTS_FILE${NC}"
fi

echo -e "${BLUE}📁 ARCHIVOS GENERADOS${NC}"
echo -e "📄 JSON Results: ${GREEN}$RESULTS_FILE${NC}"
echo -e "🌐 HTML Report: ${GREEN}$HTML_REPORT${NC}"

echo -e "${GREEN}🎉 Performance test completado exitosamente!${NC}"
echo -e "${BLUE}💡 Próximos pasos:${NC}"
echo -e "  📊 Revisa el reporte HTML para análisis detallado"
echo -e "  🔧 Optimiza endpoints con response time > 200ms"
echo -e "  📈 Ejecuta tests regularmente para tracking de performance"

# Cleanup old results (keep last 10)
echo -e "${YELLOW}🧹 Limpiando archivos antiguos...${NC}"
ls -t "$RESULTS_DIR"/* | tail -n +11 | xargs -r rm -f
echo -e "${GREEN}✅ Limpieza completada${NC}"