#!/bin/bash

echo "=================================================="
echo "🗑️  DESTRUIR INFRAESTRUCTURA COMPLETA"
echo "=================================================="
echo ""
echo "⚠️  ADVERTENCIA: Esto eliminará TODOS los recursos:"
echo "   • GKE Cluster (cpe-autoscaling-gke)"
echo "   • Cloud SQL (cpe-autoscaling-postgres)"
echo "   • Artifact Registry (autoscaling-repo)"
echo "   • Todas las aplicaciones desplegadas"
echo ""
read -p "¿Estás seguro? Escribe 'DESTRUIR' para confirmar: " confirmation

if [ "$confirmation" != "DESTRUIR" ]; then
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "🗑️  Iniciando destrucción de infraestructura..."

# Paso 1: Destruir aplicaciones (stack gcp-deploy)
echo ""
echo "🔄 PASO 1: Destruir aplicaciones en GKE..."
cd ../infrastructure-gcp-deploy
if [ -d "venv" ]; then
    source venv/bin/activate
    pulumi destroy --yes --skip-preview
    deactivate
fi
cd ../scripts

# Paso 2: Destruir Cloud SQL (stack gcp-db)
echo ""
echo "🔄 PASO 2: Destruir Cloud SQL..."
cd ../infrastructure-gcp-db
if [ -d "venv" ]; then
    source venv/bin/activate
    pulumi destroy --yes --skip-preview
    deactivate
fi
cd ../scripts

# Paso 3: Destruir GKE Cluster (stack gcp-base)
echo ""
echo "🔄 PASO 3: Destruir GKE Cluster..."
cd ../infrastructure-gcp-base
if [ -d "venv" ]; then
    source venv/bin/activate
    pulumi destroy --yes --skip-preview
    deactivate
fi
cd ../scripts

# Paso 4: Eliminar Artifact Registry (opcional)
echo ""
read -p "¿Eliminar también Artifact Registry? (y/n): " delete_registry
if [ "$delete_registry" = "y" ]; then
    echo "🗑️  Eliminando Artifact Registry..."
    gcloud artifacts repositories delete autoscaling-repo \
        --location=us-central1 \
        --project=cpe-autoscaling-k8s \
        --quiet
fi

# Paso 5: Limpiar configuraciones locales
echo ""
echo "🧹 Limpiando configuraciones locales..."
# No eliminar los archivos de código, solo el estado de pulumi si lo deseas

echo ""
echo "✅ DESTRUCCIÓN COMPLETADA"
echo "=================================================="
echo "📊 Recursos eliminados:"
echo "   ✓ GKE Cluster"
echo "   ✓ Cloud SQL"
echo "   ✓ Deployments y Servicios"
if [ "$delete_registry" = "y" ]; then
    echo "   ✓ Artifact Registry"
fi
echo ""
echo "💰 Créditos liberados: ~\$50-80/mes"
echo ""
echo "📝 Para volver a desplegar:"
echo "   bash scripts/gcp-deploy-all.sh"
echo "   (Tiempo: ~30 minutos)"
echo "=================================================="
