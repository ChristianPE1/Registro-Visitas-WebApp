#!/bin/bash
set -e

echo "=================================================="
echo "PASO 2: Desplegar Cloud SQL PostgreSQL"
echo "=================================================="

cd "$(dirname "$0")/../infrastructure-gcp-db"

if [ ! -f "__main__.py" ]; then
    echo "Error: No se encontró __main__.py"
    exit 1
fi

echo "Directorios: $(pwd)"

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

# Verificar configuración de Pulumi
echo "Verificando configuración de Pulumi..."

# Seleccionar o crear stack
if ! pulumi stack select production 2>/dev/null; then
    echo "Creando stack 'production'..."
    pulumi stack init production
fi

# Configurar proyecto de GCP
echo "Configurando proyecto GCP..."
pulumi config set gcp:project cpe-autoscaling-k8s
pulumi config set gcp:region us-central1

# Configurar password de base de datos
if ! pulumi config get db_admin_password --show-secrets > /dev/null 2>&1; then
    echo "Configurando password de base de datos..."
    DB_PASSWORD=$(openssl rand -base64 32)
    pulumi config set --secret db_admin_password "$DB_PASSWORD"
else
    echo "Password de base de datos ya configurada"
fi

echo "Configuración actual:"
pulumi config


# Desplegar
pulumi up --yes

echo "Outputs:"
pulumi stack output

echo "=================================================="
echo "✅ PASO 2 COMPLETADO"
echo "=================================================="
