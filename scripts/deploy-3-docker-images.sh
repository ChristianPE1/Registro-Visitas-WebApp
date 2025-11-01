#!/bin/bash
set -e

echo "=================================================="
echo "PASO 3: Construir y Publicar Imágenes Docker"
echo "=================================================="

PROJECT_ROOT="$(dirname "$0")/.."
cd "$PROJECT_ROOT"


# Nombre del Azure Container Registry
ACR_NAME="cpeautoscalingacr"
RESOURCE_GROUP="cpe-k8s-autoscaling-rg"

echo "Verificando si ACR existe..."

# Verificar si ACR ya existe
if az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "ACR '$ACR_NAME' ya existe"
else
    echo "Creando Azure Container Registry..."
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$ACR_NAME" \
        --sku Basic \
        --location eastus
    echo "ACR creado"
fi

# Login a ACR
echo "Login a Azure Container Registry..."
az acr login --name "$ACR_NAME"

# Construir backend
echo "Construyendo imagen del BACKEND..."
cd backend
docker build -t "${ACR_NAME}.azurecr.io/autoscaling-backend:v1" .

echo "Publicando imagen del backend..."
docker push "${ACR_NAME}.azurecr.io/autoscaling-backend:v1"

# Construir frontend
echo "Construyendo imagen del FRONTEND..."
cd ../frontend
docker build -t "${ACR_NAME}.azurecr.io/autoscaling-frontend:v1" .

echo "Publicando imagen del frontend..."
docker push "${ACR_NAME}.azurecr.io/autoscaling-frontend:v1"

# Dar permisos a AKS
echo "Dando permisos a AKS para acceder a ACR..."
az aks update \
    --resource-group "$RESOURCE_GROUP" \
    --name "cpe-k8s-autoscaling-aks" \
    --attach-acr "$ACR_NAME"

echo "Imágenes construidas y publicadas:"
echo "   - ${ACR_NAME}.azurecr.io/autoscaling-backend:v1"
echo "   - ${ACR_NAME}.azurecr.io/autoscaling-frontend:v1"

echo "=================================================="
echo "✅ PASO 3 COMPLETADO"
echo "=================================================="
