#!/bin/bash

echo "=================================================="
echo "PASO 5: Verificar Despliegue"
echo "=================================================="

PROJECT_ID="cpe-autoscaling-k8s"
ZONE="us-central1-a"

# Verificar que kubectl esté configurado
echo "Verificando conexión con GKE..."
kubectl cluster-info

echo "Estado de los nodos:"
kubectl get nodes -o wide

echo "Pods en namespace backend:"
kubectl get pods -n backend

echo "Pods en namespace frontend:"
kubectl get pods -n frontend

echo "HPAs (Horizontal Pod Autoscalers):"
kubectl get hpa -n backend
kubectl get hpa -n frontend

echo "Servicios:"
kubectl get svc -n backend
kubectl get svc -n frontend

echo "Outputs de Pulumi (infrastructure-gcp-deploy):"
cd "$(dirname "$0")/../infrastructure-gcp-deploy"
source venv/bin/activate 2>/dev/null || true
pulumi stack output

echo "URL del Frontend:"
FRONTEND_URL=$(pulumi stack output frontend_url 2>/dev/null || echo "Pendiente...")
echo "   $FRONTEND_URL"

echo "=================================================="
echo "✅ VERIFICACIÓN COMPLETA"
echo "=================================================="
