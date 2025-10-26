#!/bin/bash
# Monitor optimizado con CPU en tiempo real

RG="cpe-autoscaling-demo-rg"
VMSS="cpe-autoscaling-demo-vmss"
SUBSCRIPTION="1eb83675-114b-4f93-8921-f055b5bd6ea8"

clear
echo "=========================================="
echo "Monitor de Autoscaling - $(date '+%H:%M:%S')"
echo "=========================================="
echo ""

# Contar instancias
COUNT=$(az vmss list-instances -g $RG -n $VMSS --query "length(@)" -o tsv)
echo "Total de instancias: $COUNT"
echo ""

# Listar instancias con formato compacto
echo "ID | Estado       | Creación"
echo "---|--------------|------------------"
az vmss list-instances -g $RG -n $VMSS --query "[].{id:instanceId,state:provisioningState,time:timeCreated}" -o tsv | \
    awk '{printf "%-2s | %-12s | %s\n", $1, $2, substr($3,12,8)}'

echo ""
echo "CPU por instancia:"
echo "-----------------------------------"

# CPU agregado del VMSS completo
VMSS_CPU=$(az monitor metrics list \
    --resource "/subscriptions/$SUBSCRIPTION/resourceGroups/$RG/providers/Microsoft.Compute/virtualMachineScaleSets/$VMSS" \
    --metric "Percentage CPU" \
    --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
    --interval PT1M \
    --aggregation Average \
    --query "value[0].timeseries[0].data[-1].average" -o tsv 2>/dev/null)

if [ -n "$VMSS_CPU" ] && [ "$VMSS_CPU" != "null" ]; then
    printf "  VMSS Promedio: %.2f%%\n" "$VMSS_CPU"
else
    echo "  VMSS Promedio: Sin datos aun"
fi

# CPU por instancia individual
instances=$(az vmss list-instances -g $RG -n $VMSS --query "[].instanceId" -o tsv)
while read -r instance_id; do
    if [ -n "$instance_id" ]; then
        cpu=$(az monitor metrics list \
            --resource "/subscriptions/$SUBSCRIPTION/resourceGroups/$RG/providers/Microsoft.Compute/virtualMachineScaleSets/$VMSS/virtualMachines/$instance_id" \
            --metric "Percentage CPU" \
            --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
            --interval PT1M \
            --aggregation Average \
            --query "value[0].timeseries[0].data[-1].average" -o tsv 2>/dev/null)
        
        if [ -n "$cpu" ] && [ "$cpu" != "null" ]; then
            printf "  Instancia #%-2s: %.2f%%\n" "$instance_id" "$cpu"
        else
            printf "  Instancia #%-2s: Esperando datos...\n" "$instance_id"
        fi
    fi
done <<< "$instances"

echo ""
echo "Reglas de autoscaling:"
echo "  Scale OUT: CPU > 70% por 5 min → +1 instancia"
echo "  Scale IN:  CPU < 30% por 5 min → -1 instancia"
echo ""
echo "=========================================="
