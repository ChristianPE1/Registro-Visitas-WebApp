#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     🚀 DESPLIEGUE COMPLETO DEL SISTEMA DE AUTOSCALING     ║"
echo "║            Kubernetes (AKS) con Pulumi (IaC)              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Este script ejecutará 5 pasos en orden:"
echo "  1. ☸️  Desplegar Cluster AKS (10-15 min)"
echo "  2. 🗄️  Desplegar Base de Datos PostgreSQL (5-10 min)"
echo "  3. 🐳 Construir y Publicar Imágenes Docker (5 min)"
echo "  4. 📦 Desplegar Aplicaciones en Kubernetes (3-5 min)"
echo "  5. ✅ Verificar Despliegue (1 min)"
echo ""
echo "⏱️  Tiempo total estimado: 25-40 minutos"
echo ""

read -p "¿Continuar con el despliegue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Despliegue cancelado"
    exit 1
fi

SCRIPT_DIR="$(dirname "$0")"
START_TIME=$(date +%s)

# Paso 1
bash "$SCRIPT_DIR/deploy-1-cluster.sh"
echo ""
read -p "⏸️  Presiona Enter para continuar con el Paso 2..."
echo ""

# Paso 2
bash "$SCRIPT_DIR/deploy-2-database.sh"
echo ""
read -p "⏸️  Presiona Enter para continuar con el Paso 3..."
echo ""

# Paso 3
bash "$SCRIPT_DIR/deploy-3-docker-images.sh"
echo ""
read -p "⏸️  Presiona Enter para continuar con el Paso 4..."
echo ""

# Paso 4
bash "$SCRIPT_DIR/deploy-4-applications.sh"
echo ""
read -p "⏸️  Presiona Enter para continuar con la verificación..."
echo ""

# Paso 5
bash "$SCRIPT_DIR/deploy-5-verify.sh"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║          ✅ DESPLIEGUE COMPLETADO EXITOSAMENTE            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⏱️  Tiempo total: ${MINUTES}m ${SECONDS}s"
echo ""
echo "🎉 ¡El sistema está listo para usar!"
echo ""
