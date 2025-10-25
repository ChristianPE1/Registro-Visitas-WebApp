#!/bin/bash
# Script para verificar el estado del deployment de Azure

cd /home/christianpe/Documentos/proyectos/sistema-autoscaling/infrastructure-azure
source venv/bin/activate

echo "============================================"
echo "  ESTADO DEL DEPLOYMENT DE AZURE"
echo "============================================"
echo ""

echo "📊 OUTPUTS DEL STACK:"
echo "--------------------------------------------"
pulumi stack output
echo ""

echo "🔍 RECURSOS CREADOS:"
echo "--------------------------------------------"
pulumi stack --show-urns | head -50
echo ""

echo "🌐 VERIFICANDO LOAD BALANCER:"
echo "--------------------------------------------"
LB_IP=$(pulumi stack output load_balancer_ip 2>/dev/null)
if [ ! -z "$LB_IP" ]; then
    echo "✅ Load Balancer IP: $LB_IP"
    echo ""
    echo "🔗 Probando health check..."
    curl -s -o /dev/null -w "Status: %{http_code}\n" http://$LB_IP/health || echo "❌ No responde aún"
else
    echo "⏳ Load Balancer aún no disponible"
fi
echo ""

echo "🗄️ VERIFICANDO POSTGRESQL:"
echo "--------------------------------------------"
PG_SERVER=$(pulumi stack output postgres_server 2>/dev/null)
if [ ! -z "$PG_SERVER" ]; then
    echo "✅ PostgreSQL Server: $PG_SERVER"
else
    echo "⏳ PostgreSQL aún no disponible"
fi
echo ""

echo "🖥️ VERIFICANDO VMs:"
echo "--------------------------------------------"
VMSS_NAME=$(pulumi stack output vmss_name 2>/dev/null)
RG_NAME=$(pulumi stack output resource_group_name 2>/dev/null)
if [ ! -z "$VMSS_NAME" ] && [ ! -z "$RG_NAME" ]; then
    echo "✅ VMSS: $VMSS_NAME"
    echo ""
    echo "Instancias activas:"
    az vmss list-instances \
        --resource-group $RG_NAME \
        --name $VMSS_NAME \
        --output table 2>/dev/null || echo "⏳ VMSS aún no disponible"
else
    echo "⏳ VMSS aún no disponible"
fi
echo ""

echo "============================================"
echo "  FIN DEL REPORTE"
echo "============================================"
