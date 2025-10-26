#!/bin/bash
# Deployment Status Verification Script

if [ $# -eq 0 ]; then
    LB_IP=$(cd ~/Documentos/proyectos/sistema-autoscaling/infrastructure-azure && pulumi stack output load_balancer_ip 2>/dev/null)
    if [ -z "$LB_IP" ]; then
        echo "Error: Unable to get Load Balancer IP"
        echo "Usage: $0 <LOAD_BALANCER_IP>"
        exit 1
    fi
else
    LB_IP=$1
fi

echo "Deployment Status Check"
echo "Target: $LB_IP"
echo "---"

echo "\n1. VMSS Instances:"
az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss \
  --query '[].{Name:name, State:provisioningState}' -o table

echo "\n2. Load Balancer Health:"
az network lb show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-lb \
  --query '{Probes:probes[].name}' -o table

echo "\n3. Application Health:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$LB_IP/health 2>/dev/null)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "Flask Backend: OK (HTTP $HTTP_STATUS)"
    curl -s http://$LB_IP/health | python3 -m json.tool 2>/dev/null
else
    echo "Flask Backend: FAILED (HTTP $HTTP_STATUS)"
fi

echo "\n4. Monitoring Services:"
curl -s -o /dev/null -w "Grafana: HTTP %{http_code}\n" http://$LB_IP:3000/api/health 2>/dev/null
curl -s -o /dev/null -w "Prometheus: HTTP %{http_code}\n" http://$LB_IP:9090/-/healthy 2>/dev/null

echo "\n---"
echo "Access URLs:"
echo "  Flask: http://$LB_IP/"
echo "  Grafana: http://$LB_IP:3000"
echo "  Prometheus: http://$LB_IP:9090"
