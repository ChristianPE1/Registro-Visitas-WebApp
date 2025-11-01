#!/bin/bash
set -e

echo "=================================================="
echo "PASO 3: Construir y Subir Imágenes Docker"
echo "=================================================="

PROJECT_ID="cpe-autoscaling-k8s"
REGION="us-central1"
REPO_NAME="autoscaling-repo"

# Crear repositorio en Artifact Registry si no existe
echo "Verificando Artifact Registry..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "Creando repositorio en Artifact Registry..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --project=$PROJECT_ID \
        --description="Docker images for autoscaling demo"
    echo "Repositorio creado"
else
    echo "Repositorio ya existe"
fi

# Configurar Docker para usar Artifact Registry
echo "Configurando Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Construir y subir imagen del backend
echo "Construyendo imagen del backend..."
cd "$(dirname "$0")/../backend"
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/autoscaling-backend:v1"
docker build -t $BACKEND_IMAGE .

echo "⬆Subiendo imagen del backend..."
docker push $BACKEND_IMAGE

# Construir y subir imagen del frontend
echo "Construyendo imagen del frontend..."
cd "$(dirname "$0")/../frontend"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/autoscaling-frontend:v1"
docker build -t $FRONTEND_IMAGE .

echo "⬆Subiendo imagen del frontend..."
docker push $FRONTEND_IMAGE

echo "Imágenes construidas y subidas exitosamente"
echo "Imágenes disponibles:"
echo "   Backend:  $BACKEND_IMAGE"
echo "   Frontend: $FRONTEND_IMAGE"
echo "=================================================="
echo "✅ PASO 3 COMPLETADO"
echo "=================================================="
