#!/bin/bash

echo "=================================================="
echo "⏸️  PAUSAR DESPLIEGUE - Escalar a 0 réplicas"
echo "=================================================="

# Configuración
PROJECT_ID="cpe-autoscaling-k8s"
CLUSTER_NAME="cpe-autoscaling-gke"
ZONE="us-central1-a"

# Configurar kubectl
echo "🔧 Configurando kubectl..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project=$PROJECT_ID

echo ""
echo "⏸️  Escalando deployments a 0 réplicas..."

# Escalar backend a 0
echo "  📦 Backend: 2 → 0 réplicas"
kubectl scale deployment backend -n backend --replicas=0

# Escalar frontend a 0
echo "  🌐 Frontend: 1 → 0 réplicas"
kubectl scale deployment frontend -n frontend --replicas=0

echo ""
echo "⏸️  Eliminando HPAs temporalmente (para evitar que reescalen)..."
kubectl delete hpa backend-hpa -n backend --ignore-not-found
kubectl delete hpa frontend-hpa -n frontend --ignore-not-found

echo ""
echo "⏸️  Escalando node pool a mínimo (1 nodo)..."
gcloud container clusters resize $CLUSTER_NAME \
    --node-pool primary-pool \
    --num-nodes 1 \
    --zone $ZONE \
    --project $PROJECT_ID \
    --quiet

echo ""
echo "⏸️  Pausando Cloud SQL (esto toma ~5 minutos)..."
gcloud sql instances patch cpe-autoscaling-postgres \
    --activation-policy=NEVER \
    --project=$PROJECT_ID

echo ""
echo "✅ DESPLIEGUE PAUSADO"
echo "=================================================="
echo "📊 Estado actual:"
kubectl get pods -n backend
kubectl get pods -n frontend
echo ""
echo "💰 Costos estimados mientras está pausado:"
echo "   • GKE: ~\$20-30/mes (1 nodo e2-small)"
echo "   • Cloud SQL: \$0 (pausado)"
echo "   • Artifact Registry: ~\$0.10/mes"
echo ""
echo "▶️  Para reanudar: bash scripts/resume-deployment.sh"
echo "=================================================="
