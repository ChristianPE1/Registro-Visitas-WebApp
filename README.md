# 🚀 Sistema de Autoscaling con Kubernetes en Azure (AKS)

Sistema de demostración de autoscaling automático desplegado en Azure Kubernetes Service (AKS) con infraestructura como código usando Pulumi.

## 📐 Arquitectura

Este proyecto implementa una arquitectura **Micro-Stack** basada en los principios del libro **"Infrastructure as Code: Dynamic Systems for the Cloud Age"** de Kief Morris.

```
┌─────────────────────────────────────────────────────────────────┐
│                          AZURE CLOUD                             │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │           AKS CLUSTER (Pila 1: k8s-base)                  │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │  System Pool │  │Frontend Pool │  │ Backend Pool │   │  │
│  │  │  (1 nodo)    │  │  (1-3 nodos) │  │ (1-5 nodos)  │   │  │
│  │  │  B2s         │  │  B2s         │  │  B2s         │   │  │
│  │  │              │  │              │  │              │   │  │
│  │  │ Prometheus   │  │  Frontend    │  │  Backend     │   │  │
│  │  │ Grafana      │  │  Pods (HPA)  │  │  Pods (HPA)  │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │   PostgreSQL Flexible Server (Pila 2: k8s-db)            │  │
│  │   Tier: Burstable B1ms | Storage: 32 GiB                 │  │
│  │   Pila independiente con ciclo de vida propio            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │   Load Balancer (frontend-service)                       │  │
│  │   HTTP: 80 → Frontend | /api → Backend                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Principios de IaC Implementados

### Capítulo 1: Mentalidad de la Edad de Nube
✅ **Velocidad + Calidad**: Infraestructura reproducible = cambios rápidos y seguros  
✅ **4 Métricas DORA**: Sistema preparado para CD (despliegues frecuentes, MTTR bajo)  
✅ **Piezas pequeñas débilmente acopladas**: Frontend, backend y DB independientes

### Capítulo 2: Principios de Infraestructura
✅ **Asumir sistemas no confiables**: Pods efímeros con health checks y auto-healing  
✅ **Hacer todo reproducible**: Toda la infraestructura definida como código  
✅ **Cosas desechables (Ganado no Mascotas)**: Pods reemplazables automáticamente  
✅ **Minimizar variación**: Node pools homogéneos, todas las VMs son iguales

### Capítulo 3: Plataformas de Infraestructura
✅ **Modelo 3 capas**:
  - **IaaS**: AKS cluster, VNET, NSG (infrastructure-k8s-base)
  - **PaaS**: PostgreSQL, Node pools (infrastructure-k8s-db)
  - **Aplicaciones**: Frontend/Backend pods (infrastructure-k8s-deploy)

### Capítulo 4: Define Todo como Código
✅ **Todo en VCS**: Git como fuente de verdad, todo versionado  
✅ **Declarativo**: Pulumi + Kubernetes manifiestos (idempotentes)  
✅ **GPL sobre DSL**: Pulumi con Python (no HCL/YAML puro)

### Capítulo 5: Micro-Stack Pattern
✅ **3 Pilas Independientes**:
  1. **k8s-base**: Infraestructura base (cluster AKS)
  2. **k8s-db**: Base de datos (ciclo de vida separado)
  3. **k8s-deploy**: Aplicaciones (frontend + backend)
✅ **Radio de explosión limitado**: Cambios aislados por pila  
✅ **Ciclos de vida independientes**: Puedo reconstruir el cluster sin tocar la DB

## 📦 Estructura del Proyecto

```
sistema-autoscaling/
├── infrastructure-k8s-base/       # Pila 1: AKS Cluster (IaaS)
│   ├── __main__.py                # Cluster AKS con 3 node pools
│   ├── Pulumi.yaml
│   └── requirements.txt
│
├── infrastructure-k8s-db/         # Pila 2: Base de Datos (Micro-stack)
│   ├── __main__.py                # PostgreSQL Flexible Server
│   ├── Pulumi.yaml
│   └── requirements.txt
│
├── infrastructure-k8s-deploy/     # Pila 3: Despliegue K8s (PaaS)
│   ├── __main__.py                # Despliega backend y frontend
│   ├── Pulumi.yaml
│   └── requirements.txt
│
├── k8s/                           # Manifiestos Kubernetes
│   ├── backend/
│   │   ├── deployment.yaml        # Backend + HPA
│   │   └── README.md
│   ├── frontend/
│   │   ├── deployment.yaml        # Frontend + HPA + LoadBalancer
│   │   └── README.md
│   └── monitoring/
│       ├── prometheus-grafana.yaml
│       └── README.md
│
├── backend/                       # Código de la aplicación
│   ├── app.py                     # Flask + PostgreSQL
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                      # Código del frontend
│   ├── src/App.jsx                # React
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── scripts/                       # Scripts de pruebas de carga
│   ├── extreme-load.py
│   └── ultra-load.py
│
├── ARQUITECTURA-K8S.md            # Documentación detallada
└── README.md                      # Este archivo
```

## 🚀 Despliegue Completo

### Paso 0: Pre-requisitos
```bash
# Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login a Azure
az login

# Instalar Pulumi
curl -fsSL https://get.pulumi.com | sh

# Instalar kubectl
az aks install-cli

# Instalar Docker
sudo apt-get update && sudo apt-get install docker.io -y
```

### Paso 1: Desplegar Infraestructura Base (AKS Cluster)
```bash
cd infrastructure-k8s-base

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Login a Pulumi
pulumi login

# Crear/Seleccionar stack
pulumi stack init production

# Configurar SSH key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aks_key
pulumi config set ssh_public_key "$(cat ~/.ssh/aks_key.pub)"

# Desplegar cluster AKS
pulumi up
```

⏱️ **Tiempo estimado**: 10-15 minutos

### Paso 2: Desplegar Base de Datos
```bash
cd ../infrastructure-k8s-db

# Activar entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seleccionar stack
pulumi stack init production

# Configurar password de DB
pulumi config set --secret db_admin_password "TuPasswordSegura123!"

# Desplegar PostgreSQL
pulumi up
```

⏱️ **Tiempo estimado**: 5-10 minutos

### Paso 3: Construir y Publicar Imágenes Docker
```bash
# Crear Azure Container Registry
az acr create --resource-group cpe-k8s-autoscaling-rg \
  --name cpeautoscalingacr --sku Basic

# Login a ACR
az acr login --name cpeautoscalingacr

# Construir backend
cd ../../backend
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-backend:v1 .
docker push cpeautoscalingacr.azurecr.io/autoscaling-backend:v1

# Construir frontend
cd ../frontend
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1 .
docker push cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1

# Dar permisos a AKS
az aks update --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks \
  --attach-acr cpeautoscalingacr
```

### Paso 4: Desplegar Aplicaciones en Kubernetes
```bash
cd ../infrastructure-k8s-deploy

# Activar entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Obtener kubeconfig de AKS
az aks get-credentials --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks --overwrite-existing

# Configurar imágenes
pulumi stack init production
pulumi config set backend_image cpeautoscalingacr.azurecr.io/autoscaling-backend:v1
pulumi config set frontend_image cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1
pulumi config set --secret db_admin_password "TuPasswordSegura123!"

# Desplegar aplicaciones
pulumi up
```

⏱️ **Tiempo estimado**: 5 minutos

### Paso 5: Desplegar Monitoreo (Opcional)
```bash
# Aplicar manifiestos de Prometheus y Grafana
kubectl apply -f ../k8s/monitoring/prometheus-grafana.yaml
```

## 🔍 Verificación

```bash
# Ver todos los pods
kubectl get pods --all-namespaces

# Ver servicios (obtener IPs públicas)
kubectl get svc --all-namespaces

# Ver estado de HPA
kubectl get hpa -n backend
kubectl get hpa -n frontend

# Ver nodos del cluster
kubectl get nodes -o wide

# Obtener URL del frontend
pulumi stack output frontend_url -C infrastructure-k8s-deploy
```

## 🌐 Acceso a la Aplicación

### Frontend (React)
```bash
# Obtener IP pública
kubectl get svc -n frontend frontend-service

# Abrir en navegador
http://<EXTERNAL-IP>
```

### Grafana
```bash
kubectl get svc -n monitoring grafana-service
# http://<EXTERNAL-IP>:3000
# Usuario: admin | Contraseña: admin
```

### Prometheus
```bash
kubectl get svc -n monitoring prometheus-service
# http://<EXTERNAL-IP>:9090
```

## 📊 Autoscaling

### Horizontal Pod Autoscaler (HPA)
- **Backend**: 2-10 réplicas
  - Escala en CPU > 70%
  - Escala en RAM > 80%
- **Frontend**: 1-5 réplicas
  - Escala en CPU > 60%

### Cluster Autoscaler
- **Frontend pool**: 1-3 nodos (Standard_B2s)
- **Backend pool**: 1-5 nodos (Standard_B2s)
- **System pool**: 1 nodo fijo (Standard_B2s)

## 🧪 Pruebas de Carga

### Desde la interfaz web
1. Abrir el frontend en el navegador
2. Usar el botón "Prueba de CPU" (genera carga en backend)
3. Usar "50 Peticiones Simultáneas" (genera carga de requests)

### Desde scripts
```bash
cd scripts

# Prueba moderada
python3 extreme-load.py --url http://<FRONTEND-IP> --duration 300

# Prueba intensa
python3 ultra-load.py --url http://<FRONTEND-IP>
```

### Monitorear autoscaling en tiempo real
```bash
# En una terminal
watch kubectl get hpa -n backend

# En otra terminal
watch kubectl get pods -n backend

# Ver métricas de nodos
kubectl top nodes
kubectl top pods -n backend
```

## 💰 Costos Estimados (Azure Free Tier)

- **AKS Control Plane**: $0 (gratis)
- **System Node Pool** (1x B2s): ~$30/mes
- **Frontend Pool** (1-3x B2s): $30-90/mes
- **Backend Pool** (1-5x B2s): $30-150/mes
- **PostgreSQL B1ms**: ~$12/mes
- **Load Balancer**: ~$20/mes

**Total**: $92-302/mes (según autoscaling)

## 🗑️ Destruir Infraestructura

**Importante**: Destruir en orden inverso al despliegue.

```bash
# 1. Eliminar aplicaciones
cd infrastructure-k8s-deploy
pulumi destroy

# 2. Eliminar monitoreo (si lo desplegaste)
kubectl delete -f ../k8s/monitoring/prometheus-grafana.yaml

# 3. Eliminar base de datos (⚠️ esto borra los datos)
cd ../infrastructure-k8s-db
pulumi destroy

# 4. Eliminar cluster AKS
cd ../infrastructure-k8s-base
pulumi destroy
```

## 📚 Documentación Adicional

- [ARQUITECTURA-K8S.md](./ARQUITECTURA-K8S.md) - Arquitectura detallada
- [infrastructure-k8s-base/README.md](./infrastructure-k8s-base/README.md) - Pila 1
- [infrastructure-k8s-db/README.md](./infrastructure-k8s-db/README.md) - Pila 2
- [infrastructure-k8s-deploy/README.md](./infrastructure-k8s-deploy/README.md) - Pila 3
- [k8s/backend/README.md](./k8s/backend/README.md) - Manifiestos backend
- [k8s/frontend/README.md](./k8s/frontend/README.md) - Manifiestos frontend
- [k8s/monitoring/README.md](./k8s/monitoring/README.md) - Prometheus + Grafana

## 🔧 Tecnologías Utilizadas

- **Cloud**: Azure (AKS, PostgreSQL Flexible Server, ACR)
- **IaC**: Pulumi con Python
- **Orchestration**: Kubernetes 1.28
- **Backend**: Flask + Gunicorn + PostgreSQL
- **Frontend**: React + Vite + Nginx
- **Monitoring**: Prometheus + Grafana
- **Load Testing**: Custom Python scripts

## 📖 Referencias

- [Infrastructure as Code (Libro)](https://www.oreilly.com/library/view/infrastructure-as-code/9781098114664/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service/)
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

## 👤 Autor

Christian PE  
Proyecto de demostración de IaC y Autoscaling

## 📄 Licencia

MIT License
