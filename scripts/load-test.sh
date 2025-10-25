#!/bin/bash

# Script para generar carga externa en el servidor
# Uso: ./load-test.sh <URL> <NUM_REQUESTS> <CONCURRENT>

URL="${1:-http://localhost:5000}"
NUM_REQUESTS="${2:-1000}"
CONCURRENT="${3:-50}"

echo "🚀 Iniciando prueba de carga..."
echo "URL: $URL"
echo "Peticiones totales: $NUM_REQUESTS"
echo "Peticiones concurrentes: $CONCURRENT"
echo ""

# Verificar si Apache Bench está instalado
if ! command -v ab &> /dev/null; then
    echo "⚠️  Apache Bench (ab) no está instalado."
    echo "Instalando..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y apache2-utils
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # ab viene preinstalado en macOS
        echo "ab debería estar disponible en macOS"
    fi
fi

# Ejecutar prueba de carga en el endpoint de visitas
echo "📊 Prueba 1: Endpoint de registro de visitas"
ab -n $NUM_REQUESTS -c $CONCURRENT -p post-data.json -T application/json "$URL/api/visit"

echo ""
echo "⚡ Prueba 2: Endpoint de stress test"
ab -n 100 -c 10 -p stress-data.json -T application/json "$URL/api/stress"

echo ""
echo "✅ Pruebas completadas!"
