#!/bin/bash
set -e

echo "=================================================="
echo "🗄️ PASO 2: Desplegar Base de Datos PostgreSQL"
echo "=================================================="

# Ir al directorio correcto
cd "$(dirname "$0")/../infrastructure-k8s-db"

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

# Seleccionar o crear stack
if ! pulumi stack select production 2>/dev/null; then
    echo "📝 Creando stack 'production'..."
    pulumi stack init production
fi

# Verificar si ya existe el password configurado
if ! pulumi config get db_admin_password --show-secrets &>/dev/null; then
    echo "🔐 Obteniendo password de la configuración anterior..."
    
    # Intentar obtener password del proyecto viejo
    OLD_PASSWORD=$(cd ../infrastructure-azure && pulumi stack select production-azure 2>/dev/null && pulumi config get db_password --show-secrets 2>/dev/null || echo "")
    
    if [ -n "$OLD_PASSWORD" ]; then
        echo "✅ Password encontrado, configurando..."
        pulumi config set --secret db_admin_password "$OLD_PASSWORD"
    else
        echo "⚠️  No se encontró password anterior"
        echo "📝 Generando nuevo password seguro..."
        NEW_PASSWORD="AzureDB$(openssl rand -base64 12 | tr -d '/+=' | head -c 16)!"
        pulumi config set --secret db_admin_password "$NEW_PASSWORD"
        echo "✅ Nuevo password configurado"
    fi
else
    echo "✅ Password ya configurado"
fi

# Verificar configuración
echo ""
echo "📋 Configuración actual:"
pulumi config

echo ""
echo "⏳ Desplegando PostgreSQL (esto tomará 5-10 minutos)..."
echo ""

# Desplegar
pulumi up --yes

echo ""
echo "✅ Base de datos desplegada exitosamente"
echo ""
echo "📊 Outputs:"
pulumi stack output

echo ""
echo "=================================================="
echo "✅ PASO 2 COMPLETADO"
echo "=================================================="
