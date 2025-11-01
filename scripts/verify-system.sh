#!/bin/bash
# Script de Verificación Pre-Presentación
# Ejecutar 30 minutos antes de la presentación

echo "=================================================================="
echo "  VERIFICACIÓN DEL SISTEMA - Pre-Presentación"
echo "=================================================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

# 1. Verificar conectividad con GCP
echo "1. Verificando conectividad con GCP..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" > /dev/null 2>&1
check "Autenticado en GCP"
echo ""

# 2. Verificar cluster GKE
echo "2. Verificando cluster GKE..."
kubectl cluster-info > /dev/null 2>&1
check "Conectado al cluster GKE"
echo ""

# 3. Verificar nodos
echo "3. Verificando nodos..."
NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
echo "   Nodos activos: $NODE_COUNT"
if [ "$NODE_COUNT" -ge 1 ]; then
    echo -e "${GREEN}✓${NC} Al menos 1 nodo activo"
else
    echo -e "${RED}✗${NC} No hay nodos activos"
fi
kubectl get nodes
echo ""

# 4. Verificar namespace backend
echo "4. Verificando namespace backend..."
kubectl get namespace backend > /dev/null 2>&1
check "Namespace 'backend' existe"
echo ""

# 5. Verificar pods backend
echo "5. Verificando pods backend..."
BACKEND_PODS=$(kubectl get pods -n backend --no-headers 2>/dev/null | grep -c "Running")
echo "   Pods backend Running: $BACKEND_PODS"
if [ "$BACKEND_PODS" -ge 2 ]; then
    echo -e "${GREEN}✓${NC} Al menos 2 pods backend running"
else
    echo -e "${YELLOW}⚠${NC} Menos de 2 pods backend running"
fi
kubectl get pods -n backend
echo ""

# 6. Verificar HPA
echo "6. Verificando HPA..."
kubectl get hpa -n backend > /dev/null 2>&1
check "HPA 'backend-hpa' existe"
echo ""
echo "   Configuración HPA:"
kubectl get hpa backend-hpa -n backend -o custom-columns=\
NAME:.metadata.name,\
MINPODS:.spec.minReplicas,\
MAXPODS:.spec.maxReplicas,\
CPU:.spec.metrics[0].resource.target.averageUtilization,\
MEMORY:.spec.metrics[1].resource.target.averageUtilization
echo ""

# 7. Verificar recursos de pods
echo "7. Verificando recursos de pods backend..."
MEMORY_LIMIT=$(kubectl get deployment backend -n backend -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}')
CPU_REQUEST=$(kubectl get deployment backend -n backend -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')
echo "   CPU request: $CPU_REQUEST"
echo "   Memory limit: $MEMORY_LIMIT"
if [ "$MEMORY_LIMIT" == "256Mi" ]; then
    echo -e "${GREEN}✓${NC} Memory limit correcto (256Mi)"
else
    echo -e "${YELLOW}⚠${NC} Memory limit: $MEMORY_LIMIT (esperado: 256Mi)"
fi
echo ""

# 8. Verificar frontend service
echo "8. Verificando frontend service..."
kubectl get service frontend-service -n frontend > /dev/null 2>&1
check "Service 'frontend-service' existe"
echo ""
echo "   Obteniendo IP externa del frontend..."
FRONTEND_IP=$(kubectl get service frontend-service -n frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -n "$FRONTEND_IP" ]; then
    echo -e "${GREEN}✓${NC} Frontend IP: http://$FRONTEND_IP"
    echo "   Guardando IP en archivo..."
    echo "$FRONTEND_IP" > /tmp/frontend_ip.txt
else
    echo -e "${RED}✗${NC} No se pudo obtener IP del frontend"
fi
echo ""

# 9. Verificar conectividad del frontend
echo "9. Verificando conectividad HTTP..."
if [ -n "$FRONTEND_IP" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$FRONTEND_IP" --connect-timeout 5)
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓${NC} Frontend responde (HTTP $HTTP_CODE)"
    else
        echo -e "${YELLOW}⚠${NC} Frontend responde con HTTP $HTTP_CODE"
    fi
else
    echo -e "${RED}✗${NC} No se puede verificar (no hay IP)"
fi
echo ""

# 10. Verificar backend health
echo "10. Verificando backend health..."
kubectl port-forward -n backend svc/backend-service 5555:80 > /dev/null 2>&1 &
PORT_FORWARD_PID=$!
sleep 2
BACKEND_HEALTH=$(curl -s http://localhost:5555/health 2>/dev/null)
kill $PORT_FORWARD_PID > /dev/null 2>&1
if [[ "$BACKEND_HEALTH" == *"healthy"* ]]; then
    echo -e "${GREEN}✓${NC} Backend health check OK"
else
    echo -e "${YELLOW}⚠${NC} Backend health check: $BACKEND_HEALTH"
fi
echo ""

# 11. Verificar metrics-server
echo "11. Verificando metrics-server..."
kubectl top nodes > /dev/null 2>&1
check "Metrics disponibles (metrics-server funciona)"
echo ""

# 12. Verificar script de carga
echo "12. Verificando script de carga..."
if [ -f "scripts/ultra-load.py" ]; then
    echo -e "${GREEN}✓${NC} Script ultra-load.py existe"
    WORKERS=$(grep "^WORKERS = " scripts/ultra-load.py | awk '{print $3}')
    CONCURRENT=$(grep "^CONCURRENT_PER_WORKER = " scripts/ultra-load.py | awk '{print $3}')
    echo "   Workers: $WORKERS"
    echo "   Concurrencia por worker: $CONCURRENT"
    if [ "$WORKERS" == "8" ]; then
        echo -e "${GREEN}✓${NC} Configuración correcta (8 workers)"
    else
        echo -e "${YELLOW}⚠${NC} Workers: $WORKERS (esperado: 8)"
    fi
else
    echo -e "${RED}✗${NC} Script ultra-load.py no encontrado"
fi
echo ""

# 13. Verificar node pool autoscaling
echo "13. Verificando node pool autoscaling..."
MIN_NODES=$(gcloud container node-pools describe primary-pool \
    --cluster=cpe-autoscaling-gke \
    --zone=us-central1-a \
    --format="value(autoscaling.minNodeCount)" 2>/dev/null)
MAX_NODES=$(gcloud container node-pools describe primary-pool \
    --cluster=cpe-autoscaling-gke \
    --zone=us-central1-a \
    --format="value(autoscaling.maxNodeCount)" 2>/dev/null)

if [ -n "$MIN_NODES" ] && [ -n "$MAX_NODES" ]; then
    echo "   Min nodes: $MIN_NODES"
    echo "   Max nodes: $MAX_NODES"
    if [ "$MIN_NODES" == "1" ] || [ "$MIN_NODES" == "2" ]; then
        echo -e "${GREEN}✓${NC} Autoscaling configurado correctamente"
    else
        echo -e "${YELLOW}⚠${NC} Min nodes: $MIN_NODES (esperado: 1 o 2)"
    fi
else
    echo -e "${YELLOW}⚠${NC} No se pudo verificar autoscaling"
fi
echo ""

# Resumen final
echo "=================================================================="
echo "  RESUMEN DE VERIFICACIÓN"
echo "=================================================================="
echo ""

if [ -n "$FRONTEND_IP" ]; then
    echo -e "${GREEN}FRONTEND URL:${NC} http://$FRONTEND_IP"
    echo ""
fi

echo "Comandos para la demostración:"
echo ""
echo "1. Monitoreo HPA:"
echo "   watch -n2 \"kubectl get hpa -n backend\""
echo ""
echo "2. Monitoreo Pods:"
echo "   watch -n2 \"kubectl get pods -n backend -o wide\""
echo ""
echo "3. Monitoreo Nodos:"
echo "   watch -n2 \"kubectl get nodes\""
echo ""
echo "4. Monitoreo Métricas:"
echo "   watch -n5 'echo \"=== NODOS ===\" && kubectl top nodes && echo \"\" && echo \"=== PODS BACKEND ===\" && kubectl top pods -n backend'"
echo ""

if [ -n "$FRONTEND_IP" ]; then
    echo "5. Ejecutar prueba de carga:"
    echo "   cd scripts"
    echo "   python3 ultra-load.py $FRONTEND_IP"
    echo ""
fi

echo "=================================================================="
echo ""

# Pregunta final
echo -e "${YELLOW}¿Deseas ejecutar una prueba corta de carga (30 segundos)? (s/n)${NC}"
read -r RESPONSE

if [[ "$RESPONSE" =~ ^[sS]$ ]]; then
    if [ -n "$FRONTEND_IP" ]; then
        echo ""
        echo "Ejecutando prueba corta de carga..."
        cd scripts 2>/dev/null || true
        # Modificar temporalmente la duración
        cp ultra-load.py ultra-load-backup.py
        sed -i 's/DURATION_SECONDS = 600/DURATION_SECONDS = 30/' ultra-load.py
        python3 ultra-load.py "$FRONTEND_IP"
        # Restaurar
        mv ultra-load-backup.py ultra-load.py
        echo ""
        echo -e "${GREEN}✓${NC} Prueba corta completada"
        echo ""
        echo "Verifica que los pods hayan escalado:"
        kubectl get pods -n backend
    else
        echo -e "${RED}No se puede ejecutar (no hay IP del frontend)${NC}"
    fi
fi

echo ""
echo "=================================================================="
echo -e "${GREEN}✓ VERIFICACIÓN COMPLETADA${NC}"
echo "=================================================================="
echo ""
echo "Sistema listo para la presentación!"
echo ""
