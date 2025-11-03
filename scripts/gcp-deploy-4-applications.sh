#!/bin/bash
set -e

echo "=================================================="
echo "PASO 4: Desplegar Aplicaciones en GKE"
echo "=================================================="

PROJECT_ID="cpe-autoscaling-k8s"
REGION="us-central1"
ZONE="us-central1-a"
REPO_NAME="autoscaling-repo"

cd "$(dirname "$0")/../infrastructure-gcp-deploy"

if [ ! -f "__main__.py" ]; then
    echo "Error: No se encontró __main__.py"
    exit 1
fi

echo "Directorio: $(pwd)"

# Crear y activar entorno virtual
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -q -r requirements.txt

# Seleccionar o crear stack
if ! pulumi stack select production 2>/dev/null; then
    echo "Creando stack 'production'..."
    pulumi stack init production
fi

# Configurar proyecto de GCP
echo "Configurando proyecto GCP..."
pulumi config set gcp:project $PROJECT_ID

# Obtener kubeconfig para GKE
echo "Configurando kubectl para GKE..."
gcloud container clusters get-credentials cpe-autoscaling-gke \
    --zone=$ZONE \
    --project=$PROJECT_ID

# Verificar conectividad
echo "Verificando conectividad con GKE..."
kubectl cluster-info

# Configurar imágenes Docker
echo "Configurando imágenes Docker..."
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/autoscaling-backend:v1"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/autoscaling-frontend:v1"

pulumi config set backend_image "$BACKEND_IMAGE"
pulumi config set frontend_image "$FRONTEND_IMAGE"

# Obtener password de base de datos del stack anterior
echo "Obteniendo password de base de datos..."
cd ../infrastructure-gcp-db
source venv/bin/activate
DB_PASSWORD=$(pulumi stack output --show-secrets connection_string | grep -oP 'postgres:\K[^@]+')
cd ../infrastructure-gcp-deploy
source venv/bin/activate

if [ -z "$DB_PASSWORD" ]; then
    echo "No se pudo obtener password automáticamente"
    cd ../infrastructure-gcp-db
    source venv/bin/activate
    DB_PASSWORD=$(pulumi config get db_admin_password --show-secrets)
    cd ../infrastructure-gcp-deploy
    source venv/bin/activate
fi

pulumi config set --secret db_admin_password "$DB_PASSWORD"

echo "Configuración actual:"
pulumi config

# Intentar desplegar
echo "Desplegando aplicaciones..."
if ! pulumi up --yes 2>&1 | tee /tmp/pulumi-deploy.log; then
    # Si falla, verificar si es por cluster unreachable
    if grep -q "configured Kubernetes cluster is unreachable" /tmp/pulumi-deploy.log; then
        echo "Detectado error: cluster antiguo inaccesible"
        echo "Limpiando recursos olvidados del anterior state..."
        
        # Limpiar recursos del cluster antiguo
        PULUMI_K8S_DELETE_UNREACHABLE=true pulumi refresh --yes
        
        echo "State limpio. Reintentando deployment..."
        
        # Reintentar deployment
        pulumi up --yes
    else
        echo "Error en deployment. Revisa los logs arriba."
        exit 1
    fi
fi

echo "Outputs:"
pulumi stack output

echo "URL del frontend:"
pulumi stack output frontend_url

echo "=================================================="
echo "✅ PASO 4 COMPLETADO"
echo "=================================================="
