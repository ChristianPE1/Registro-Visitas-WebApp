#!/bin/bash
clear

# Obtener lista de instancias
instances=$(az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss --query "[].{id:instanceId,name:name}" -o tsv)

echo "Instancias activas:"
az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table
echo ""

# CPU por instancia
echo "CPU por instancia (cada minuto):"
while IFS=$'\t' read -r instance_id name; do
    cpu=$(az monitor metrics list \
        --resource "/subscriptions/1eb83675-114b-4f93-8921-f055b5bd6ea8/resourceGroups/cpe-autoscaling-demo-rg/providers/Microsoft.Compute/virtualMachineScaleSets/cpe-autoscaling-demo-vmss/virtualMachines/$instance_id" \
        --metric "Percentage CPU" \
        --start-time $(date -u -d '1 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
        --interval PT1M \
        --query "value[0].timeseries[0].data[-1].average" -o tsv 2>/dev/null)
    
    if [ -n "$cpu" ]; then
        printf "  Instancia %s: %.2f%%\n" "$instance_id" "$cpu"
    else
        printf "  Instancia %s: Sin datos\n" "$instance_id"
    fi
done <<< "$instances"

echo ""
echo "Actualizado: $(date '+%H:%M:%S')"
