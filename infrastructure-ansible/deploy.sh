#!/bin/bash

# Script para desplegar infraestructura en Azure

set -e

cd "$(dirname "$0")"

export MYSQL_PASSWORD="${MYSQL_PASSWORD:-Autoscaling2024!}"

echo "=========================================="
echo "  Desplegando infraestructura en Azure"
echo "=========================================="
echo ""

# Activar entorno virtual
source venv/bin/activate

# Desplegar toda la infraestructura
ansible-playbook deploy-all.yml

echo ""
echo "=========================================="
echo "  Despliegue completado!"
echo "=========================================="
