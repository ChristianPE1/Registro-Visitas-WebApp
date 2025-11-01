#!/bin/bash
set -e


# Hacer scripts ejecutables
chmod +x "$(dirname "$0")/gcp-deploy-"*.sh

# Paso 1: GKE Cluster
bash "$(dirname "$0")/gcp-deploy-1-cluster.sh"
echo ""
read -p "Presiona Enter para continuar con el Paso 2..."
echo ""

# Paso 2: Cloud SQL
bash "$(dirname "$0")/gcp-deploy-2-database.sh"
echo ""
read -p "Presiona Enter para continuar con el Paso 3..."
echo ""

# Paso 3: Docker Images
bash "$(dirname "$0")/gcp-deploy-3-docker-images.sh"
echo ""
read -p "Presiona Enter para continuar con el Paso 4..."
echo ""

# Paso 4: Aplicaciones
bash "$(dirname "$0")/gcp-deploy-4-applications.sh"
echo ""
read -p "Presiona Enter para continuar con el Paso 5..."
echo ""

# Paso 5: Verificación
bash "$(dirname "$0")/gcp-deploy-5-verify.sh"


echo ""
echo "====================================="
echo "DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "====================================="
echo ""
echo "Aplicación lista en:"
cd "$(dirname "$0")/../infrastructure-gcp-deploy"
source venv/bin/activate 2>/dev/null || true
pulumi stack output frontend_url
echo ""
echo "====================================="
