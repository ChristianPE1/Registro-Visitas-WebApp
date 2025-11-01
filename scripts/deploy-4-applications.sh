#!/bin/bash
set -e

echo "=================================================="
echo "PASO 4: Desplegar Aplicaciones en Kubernetes"
echo "=================================================="

# Ir al directorio correcto
cd "$(dirname "$0")/../infrastructure-k8s-deploy"

if [ ! -f "__main__.py" ]; then
    echo "Error: No se encontró __main__.py"
    exit 1
fi


# Crear y activar entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -q -r requirements.txt

# Obtener kubeconfig
echo "Obteniendo credenciales de Kubernetes..."
az aks get-credentials \
    --resource-group cpe-k8s-autoscaling-rg \
    --name cpe-k8s-autoscaling-aks \
    --overwrite-existing

# Verificar conexión
echo "Verificando conexión con cluster..."
kubectl get nodes

# Seleccionar o crear stack
if ! pulumi stack select production 2>/dev/null; then
    echo "Creando stack 'production'..."
    pulumi stack init production
fi

# Configurar imágenes Docker
ACR_NAME="cpeautoscalingacr"
echo "Configurando imágenes Docker..."
pulumi config set backend_image "${ACR_NAME}.azurecr.io/autoscaling-backend:v1"
pulumi config set frontend_image "${ACR_NAME}.azurecr.io/autoscaling-frontend:v1"

# Obtener password de la pila de DB
echo "Obteniendo password de base de datos..."
DB_PASSWORD=$(cd ../infrastructure-k8s-db && pulumi config get db_admin_password --show-secrets)
pulumi config set --secret db_admin_password "$DB_PASSWORD"

# Verificar configuración
echo "Configuración actual:"
pulumi config

# Desplegar
pulumi up --yes

echo "Outputs:"
pulumi stack output

echo ""
echo "URL del Frontend:"
pulumi stack output frontend_url 2>/dev/null || echo "   (Esperando IP pública...)"

echo ""
echo "=================================================="
echo "✅ PASO 4 COMPLETADO"
echo "=================================================="
