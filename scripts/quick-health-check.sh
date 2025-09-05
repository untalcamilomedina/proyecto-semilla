#!/bin/bash

echo "🔍 PROYECTO SEMILLA - QUICK HEALTH CHECK"
echo "======================================"
echo "Fecha: $(date)"
echo ""

# Check if backend is responding
echo "🌐 Backend Health Check:"
if curl -s -f http://localhost:7777/health > /dev/null 2>&1; then
    echo "✅ Backend: HEALTHY"
else
    echo "❌ Backend: UNHEALTHY"
fi

# Check if API is responding
echo "🔌 API Endpoints Check:"
if curl -s -f http://localhost:7777/api/v1/articles > /dev/null 2>&1; then
    echo "✅ Articles API: RESPONDING"
else
    echo "❌ Articles API: NOT RESPONDING"
fi

# Check Docker containers
echo "🐳 Docker Containers:"
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "✅ Containers: RUNNING"
    docker-compose ps --services 2>/dev/null || echo "  Unable to list services"
else
    echo "❌ Containers: NOT RUNNING"
fi

echo ""
echo "📊 Performance Test:"
response_time=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:7777/api/v1/articles 2>/dev/null || echo "N/A")
if [ "$response_time" != "N/A" ]; then
    echo "Response Time: ${response_time}s"
    if [ "$(echo "$response_time < 0.1" | awk '{if($1 < 0.1) print "yes"; else print "no"}')" = "yes" ]; then
        echo "✅ Performance: EXCELLENT (<100ms)"
    else
        echo "⚠️  Performance: ACCEPTABLE (>100ms)"
    fi
else
    echo "Response Time: Unable to measure"
fi

echo ""
echo "🎯 PRODUCTION READINESS STATUS"
echo "=============================="

# Overall assessment
backend_ok=$(curl -s -f http://localhost:7777/health > /dev/null 2>&1 && echo "yes" || echo "no")
api_ok=$(curl -s -f http://localhost:7777/api/v1/articles > /dev/null 2>&1 && echo "yes" || echo "no")
containers_ok=$(docker-compose ps 2>/dev/null | grep -q "Up" 2>/dev/null && echo "yes" || echo "no")

if [ "$backend_ok" = "yes" ] && [ "$api_ok" = "yes" ] && [ "$containers_ok" = "yes" ]; then
    echo "🎉 STATUS: PRODUCTION READY"
    echo "✅ All critical systems operational"
    exit 0
else
    echo "⚠️  STATUS: ISSUES DETECTED"
    echo "❌ Some systems need attention"
    exit 1
fi