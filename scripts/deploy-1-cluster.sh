#!/bin/bash
set -e  # Salir si hay error

echo "=================================================="
echo "🚀 PASO 1: Desplegar Cluster AKS"
echo "=================================================="

# Ir al directorio correcto
cd "$(dirname "$0")/../infrastructure-k8s-base"

# Verificar que estamos en el lugar correcto
if [ ! -f "__main__.py" ]; then
    echo "❌ Error: No se encontró __main__.py"
    exit 1
fi

echo "📍 Directorio: $(pwd)"

# Crear y activar entorno virtual
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -q -r requirements.txt

# Verificar configuración de Pulumi
echo "🔍 Verificando configuración de Pulumi..."

# Seleccionar o crear stack
if ! pulumi stack select production 2>/dev/null; then
    echo "📝 Creando stack 'production'..."
    pulumi stack init production
fi

# Verificar si existe SSH key
if [ ! -f "$HOME/.ssh/aks_key.pub" ]; then
    echo "🔑 Generando SSH key..."
    ssh-keygen -t rsa -b 4096 -f "$HOME/.ssh/aks_key" -N ""
fi

# Configurar SSH key
echo "🔑 Configurando SSH key..."
pulumi config set ssh_public_key "$(cat $HOME/.ssh/aks_key.pub)"

# Verificar configuración
echo ""
echo "📋 Configuración actual:"
pulumi config

echo ""
echo "⏳ Desplegando cluster AKS (esto tomará 10-15 minutos)..."
echo ""

# Desplegar
pulumi up --yes

echo ""
echo "✅ Cluster AKS desplegado exitosamente"
echo ""
echo "📊 Outputs:"
pulumi stack output

echo ""
echo "=================================================="
echo "✅ PASO 1 COMPLETADO"
echo "=================================================="
