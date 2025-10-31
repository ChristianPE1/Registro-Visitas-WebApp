# Pila 1: Infraestructura Base - AKS Cluster

## 📋 Descripción
Crea la infraestructura base en Azure:
- AKS Cluster con Kubernetes 1.28
- 3 Node Pools: system, frontend, backend
- Virtual Network con subnet dedicada
- Network Security Group

## 🎯 Principios IaC Aplicados
- **Define todo como código** (Cap 4): Todo en Python + Pulumi
- **Hacer reproducible** (Cap 2): Pila idempotente y versionada
- **Minimizar variación** (Cap 2): Node pools homogéneos
- **IaaS Layer** (Cap 3): Recursos fundamentales de la nube

## 🚀 Despliegue

### Pre-requisitos
```bash
# Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login a Azure
az login

# Configurar subscripción
az account set --subscription "1eb83675-114b-4f93-8921-f055b5bd6ea8"

# Instalar Pulumi
curl -fsSL https://get.pulumi.com | sh
```

### Configuración
```bash
cd infrastructure-k8s-base

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Login a Pulumi
pulumi login

# Seleccionar/crear stack
pulumi stack init production
# o
pulumi stack select production

# Configurar SSH key (generar si no tienes)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aks_key
pulumi config set ssh_public_key "$(cat ~/.ssh/aks_key.pub)"
```

### Desplegar
```bash
# Preview de cambios
pulumi preview

# Desplegar infraestructura
pulumi up

# Ver outputs
pulumi stack output
```

### Conectarse al cluster
```bash
# Obtener credenciales de kubectl
az aks get-credentials --resource-group cpe-k8s-autoscaling-rg --name cpe-k8s-autoscaling-aks

# Verificar conexión
kubectl get nodes
kubectl get pods --all-namespaces
```

## 📊 Recursos Creados
- **Resource Group**: cpe-k8s-autoscaling-rg
- **AKS Cluster**: cpe-k8s-autoscaling-aks
- **Node Pools**:
  - `systempool`: 1 nodo Standard_B2s (fijo)
  - `frontend`: 1-3 nodos Standard_B2s (autoscaling)
  - `backend`: 1-5 nodos Standard_B2s (autoscaling)
- **Virtual Network**: 10.0.0.0/16
- **Subnet AKS**: 10.0.1.0/24
- **Network Security Group**: Reglas HTTP/HTTPS/Monitoreo

## 💰 Costo Estimado
- AKS Control Plane: **$0** (Free Tier)
- Node systempool: ~$30/mes
- Node frontend (min): ~$30/mes
- Node backend (min): ~$30/mes
- **Total mínimo**: ~$90/mes

## 🗑️ Destruir
```bash
# Eliminar toda la infraestructura
pulumi destroy

# Confirmar con "yes"
```

## 🔗 Siguiente Paso
Una vez desplegado, continuar con:
- **Pila 2**: infrastructure-k8s-db (Base de datos PostgreSQL)
