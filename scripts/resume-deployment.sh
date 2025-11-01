#!/bin/bash

echo "=================================================="
echo "▶️  REANUDAR DESPLIEGUE - Encender servicios"
echo "=================================================="

# Configuración
PROJECT_ID="cpe-autoscaling-k8s"
CLUSTER_NAME="cpe-autoscaling-gke"
ZONE="us-central1-a"
DB_INSTANCE="cpe-autoscaling-postgres"

# Configurar kubectl
echo "🔧 Configurando kubectl..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project=$PROJECT_ID

echo ""
echo "🔄 PASO 1: Reactivar Cloud SQL (~2-3 minutos)..."
gcloud sql instances patch $DB_INSTANCE \
    --activation-policy=ALWAYS \
    --project=$PROJECT_ID

echo "⏳ Esperando a que Cloud SQL esté listo..."
while [[ $(gcloud sql instances describe $DB_INSTANCE --project=$PROJECT_ID --format="value(state)") != "RUNNABLE" ]]; do
    echo "   Esperando... (estado: $(gcloud sql instances describe $DB_INSTANCE --project=$PROJECT_ID --format='value(state)'))"
    sleep 10
done
echo "✅ Cloud SQL activa"

echo ""
echo "🔄 PASO 2: Escalar node pool a 2 nodos..."
gcloud container clusters resize $CLUSTER_NAME \
    --node-pool primary-pool \
    --num-nodes 2 \
    --zone $ZONE \
    --project $PROJECT_ID \
    --quiet

echo "⏳ Esperando a que los nodos estén listos..."
sleep 30
kubectl wait --for=condition=Ready nodes --all --timeout=120s

echo ""
echo "🔄 PASO 3: Recrear HPAs..."

# Recrear HPA del backend
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF

# Recrear HPA del frontend
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: frontend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
EOF

echo ""
echo "🔄 PASO 4: Escalar deployments..."

# Escalar backend a 2
echo "  📦 Backend: 0 → 2 réplicas"
kubectl scale deployment backend -n backend --replicas=2

# Escalar frontend a 1
echo "  🌐 Frontend: 0 → 1 réplicas"
kubectl scale deployment frontend -n frontend --replicas=1

echo ""
echo "⏳ Esperando a que los pods estén listos..."
kubectl wait --for=condition=Ready pod -l app=backend -n backend --timeout=120s
kubectl wait --for=condition=Ready pod -l app=frontend -n frontend --timeout=120s

echo ""
echo "✅ DESPLIEGUE REANUDADO"
echo "=================================================="
echo "📊 Estado actual:"
echo ""
echo "🔹 Nodos:"
kubectl get nodes
echo ""
echo "🔹 Pods Backend:"
kubectl get pods -n backend
echo ""
echo "🔹 Pods Frontend:"
kubectl get pods -n frontend
echo ""
echo "🔹 HPAs:"
kubectl get hpa -n backend
kubectl get hpa -n frontend
echo ""
echo "🌐 URL del Frontend:"
FRONTEND_IP=$(kubectl get service frontend-service -n frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "   http://$FRONTEND_IP"
echo ""
echo "⏱️  Tiempo total de reinicio: ~2-3 minutos"
echo "=================================================="
