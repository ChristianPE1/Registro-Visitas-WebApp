#!/bin/bash

# Script de instalación y configuración para Ansible + Azure

echo "=========================================="
echo "  Instalación de Ansible para Azure"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 no está instalado. Por favor instálalo primero.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 encontrado: $(python3 --version)${NC}"
echo ""

# Verificar pip
echo -e "${YELLOW}Verificando pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Instalando pip...${NC}"
    sudo apt update
    sudo apt install -y python3-pip
fi
echo -e "${GREEN}✓ pip encontrado: $(pip3 --version)${NC}"
echo ""

# Instalar dependencias de Python
echo -e "${YELLOW}Instalando dependencias de Python...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencias de Python instaladas${NC}"
echo ""

# Instalar colecciones de Ansible
echo -e "${YELLOW}Instalando colecciones de Ansible...${NC}"
ansible-galaxy collection install -r requirements.yml
echo -e "${GREEN}✓ Colecciones de Ansible instaladas${NC}"
echo ""

# Verificar Azure CLI
echo -e "${YELLOW}Verificando Azure CLI...${NC}"
if ! command -v az &> /dev/null; then
    echo -e "${YELLOW}Azure CLI no encontrado. ¿Deseas instalarlo? (s/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        echo -e "${YELLOW}Instalando Azure CLI...${NC}"
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
        echo -e "${GREEN}✓ Azure CLI instalado${NC}"
    else
        echo -e "${YELLOW}⚠ Azure CLI no instalado. Necesitarás instalarlo manualmente.${NC}"
    fi
else
    echo -e "${GREEN}✓ Azure CLI encontrado: $(az --version | head -n 1)${NC}"
fi
echo ""

# Verificar autenticación de Azure
echo -e "${YELLOW}Verificando autenticación de Azure...${NC}"
if az account show &> /dev/null; then
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo -e "${GREEN}✓ Autenticado en Azure${NC}"
    echo -e "  Suscripción activa: ${GREEN}$SUBSCRIPTION${NC}"
else
    echo -e "${YELLOW}⚠ No estás autenticado en Azure${NC}"
    echo -e "  Ejecuta: ${YELLOW}az login${NC}"
fi
echo ""

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creando archivo .env desde .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠ IMPORTANTE: Edita el archivo .env con tus credenciales${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi
echo ""

# Verificar Ansible
echo -e "${YELLOW}Verificando instalación de Ansible...${NC}"
if command -v ansible-playbook &> /dev/null; then
    echo -e "${GREEN}✓ Ansible encontrado: $(ansible --version | head -n 1)${NC}"
else
    echo -e "${RED}✗ Ansible no encontrado. Hay un problema con la instalación.${NC}"
    exit 1
fi
echo ""

# Resumen
echo "=========================================="
echo -e "${GREEN}  ✓ Instalación Completada${NC}"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Autenticarse en Azure:"
echo -e "   ${YELLOW}az login${NC}"
echo ""
echo "2. Editar variables de configuración:"
echo -e "   ${YELLOW}nano group_vars/all.yml${NC}"
echo ""
echo "3. Configurar credenciales (opcional):"
echo -e "   ${YELLOW}nano .env${NC}"
echo ""
echo "4. Desplegar infraestructura:"
echo -e "   ${YELLOW}ansible-playbook deploy-all.yml${NC}"
echo ""
echo "Para más información, consulta el README.md"
echo ""
