# 🚀 Sistema de Autoscaling con Kubernetes (GKE / AKS)

Sistema de demostración de autoscaling automático desplegado en Google Kubernetes Engine (GKE) o Azure Kubernetes Service (AKS) con infraestructura como código usando Pulumi.

> **Nota**: Este proyecto soporta tanto GCP como Azure. Las instrucciones actuales están enfocadas en **GCP (GKE)**. Para Azure, consulta las carpetas `infrastructure-k8s-*`.

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

### Opción A: Despliegue Automatizado en GCP (Recomendado)

**Pre-requisitos**:
```bash
# Instalar gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login a GCP
gcloud auth login
gcloud auth application-default login

# Configurar proyecto
gcloud config set project cpe-autoscaling-k8s

# Instalar Pulumi
curl -fsSL https://get.pulumi.com | sh

# Instalar kubectl
gcloud components install kubectl

# Instalar Docker
sudo apt-get update && sudo apt-get install docker.io -y

# Instalar plugin de autenticación GKE
gcloud components install gke-gcloud-auth-plugin
```

**Despliegue automatizado** (todos los pasos):
```bash
cd scripts

# Desplegar todo (cluster, DB, imágenes, apps)
bash gcp-deploy-all.sh
```

⏱️ **Tiempo total**: 35-40 minutos

**Pasos individuales** (si prefieres control manual):
```bash
# Paso 1: Cluster GKE (12-15 min)
bash gcp-deploy-1-cluster.sh

# Paso 2: Cloud SQL (15 min)
bash gcp-deploy-2-database.sh

# Paso 3: Imágenes Docker (3-5 min)
bash gcp-deploy-3-docker-images.sh

# Paso 4: Aplicaciones K8s (2-3 min)
bash gcp-deploy-4-applications.sh

# Paso 5: Verificación (1 min)
bash gcp-deploy-5-verify.sh
```

**Obtener URL del frontend**:
```bash
kubectl get svc frontend-service -n frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# O desde Pulumi:
cd infrastructure-gcp-deploy
pulumi stack output frontend_url
```

---

### Opción B: Despliegue Manual en Azure (Legacy)

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

**IMPORTANTE**: `kubectl` solo se usa para **observar** lo que Pulumi creó. Todo se ejecuta desde tu laptop local.

```bash
# 1. Obtener credenciales del cluster (una sola vez)
az aks get-credentials --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks --overwrite-existing

# 2. Ver recursos creados POR PULUMI (solo observación)
kubectl get pods --all-namespaces          # Ver pods
kubectl get svc --all-namespaces           # Ver servicios
kubectl get hpa -n backend                 # Ver autoscalers
kubectl get nodes -o wide                  # Ver nodos

# 3. Obtener URL del frontend (desde Pulumi, preferido)
cd infrastructure-k8s-deploy
pulumi stack output frontend_url
```

**kubectl NO crea infraestructura**, solo permite ver el estado del cluster remoto.

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

## � Troubleshooting

### Error: "configured Kubernetes cluster is unreachable"

**Síntoma**: Al ejecutar `pulumi up` en el stack de deploy, aparece:
```
error: configured Kubernetes cluster is unreachable: unable to load schema information from the API server: 
Get "https://<OLD_IP>/openapi/v2?timeout=32s": dial tcp <OLD_IP>:443: i/o timeout
```

**Causa**: El Pulumi state tiene referencias a un cluster antiguo que fue destruido y recreado con una nueva IP. Pulumi intenta eliminar recursos del cluster viejo antes de crear en el nuevo.

**Solución automática** (incluida en script `gcp-deploy-4-applications.sh`):
```bash
cd infrastructure-gcp-deploy  # o infrastructure-k8s-deploy para Azure
source venv/bin/activate

# Limpiar recursos huérfanos del state
PULUMI_K8S_DELETE_UNREACHABLE=true pulumi refresh --yes

# Redeployar
pulumi up --yes
```

**Solución manual** (si el script falla):
```bash
# Opción 1: Eliminar recursos específicos del state
pulumi state delete 'kubernetes:core/v1:Service::backend-service'
pulumi state delete 'kubernetes:core/v1:Service::frontend-service'
# ... (repetir para cada recurso huérfano)

# Opción 2: Destruir y recrear el stack completo
pulumi stack rm production --yes
pulumi stack init production
# Reconfigurar (backend_image, frontend_image, db_password)
pulumi up --yes
```

### Error: "Failed to create deployment" o pods en estado "ImagePullBackOff"

**Causa**: Las imágenes Docker no están disponibles en el registry o faltan permisos.

**Solución**:
```bash
# Para GCP:
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push <IMAGE_URL>

# Para Azure:
az acr login --name <ACR_NAME>
docker push <IMAGE_URL>

# Verificar que la imagen existe
docker images | grep autoscaling

# Verificar permisos (GCP)
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member=serviceAccount:<SA>@<PROJECT>.iam.gserviceaccount.com \
  --role=roles/artifactregistry.reader

# Verificar permisos (Azure)
az aks update -g <RG> -n <CLUSTER> --attach-acr <ACR_NAME>
```

### Error: HPA muestra "unknown" en targets

**Causa**: `metrics-server` no está instalado o no está funcionando.

**Solución**:
```bash
# Verificar si existe
kubectl get deployment metrics-server -n kube-system

# Instalar si falta (GKE lo incluye por defecto)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Para clusters locales (minikube, kind):
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# Verificar métricas
kubectl top nodes
kubectl top pods -n backend
```

### Pods no escalan aunque HPA esté configurado

**Causas posibles**:
1. **Umbrales demasiado altos**: CPU/memoria nunca alcanzan el target
2. **Requests no configurados**: HPA necesita `resources.requests` en el pod
3. **Carga insuficiente**: La aplicación no genera suficiente presión

**Solución**:
```bash
# 1. Verificar configuración actual del HPA
kubectl describe hpa backend-hpa -n backend

# 2. Ajustar umbrales (ejemplo: reducir CPU de 70% a 60%)
kubectl patch hpa backend-hpa -n backend --type='json' -p='[
  {"op": "replace", "path": "/spec/metrics/0/resource/target/averageUtilization", "value": 60}
]'

# 3. Verificar que los pods tienen requests configurados
kubectl get deployment backend -n backend -o yaml | grep -A 3 requests

# 4. Generar carga para probar
cd scripts
python3 ultra-load.py <FRONTEND_IP>
```

### Nodos no escalan (Cluster Autoscaler)

**Causas posibles**:
1. **Pods caben en nodos existentes**: Cluster Autoscaler solo añade nodos si hay pods Pending
2. **Limits muy altos**: Muchos pods caben por nodo, nunca hay Pending
3. **Max node count alcanzado**: Node pool llegó al límite

**Solución**:
```bash
# 1. Verificar pods en estado Pending
kubectl get pods -A | grep Pending

# 2. Verificar configuración del node pool (GCP)
gcloud container node-pools describe primary-pool \
  --cluster=<CLUSTER_NAME> --zone=<ZONE>

# 3. Reducir memory limits para aumentar densidad de pods
kubectl set resources deployment backend -n backend \
  --limits=cpu=500m,memory=256Mi \
  --requests=cpu=100m,memory=128Mi

# 4. Verificar eventos del Cluster Autoscaler
kubectl get events -n kube-system --sort-by='.lastTimestamp' | grep -i scale

# 5. Forzar creación de pods para demostrar scaling
kubectl scale deployment backend -n backend --replicas=15
```

## �🗑️ Destruir Infraestructura

**Importante**: Destruir en orden inverso al despliegue.

**Para GCP** (usa el script automatizado):
```bash
cd scripts
bash destroy-all.sh
```

**Para Azure** (manual):
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

## � CI/CD con GitHub Actions

Este proyecto incluye workflows automatizados de CI/CD que despliegan automáticamente los cambios siguiendo el patrón **Micro-Stacks**.

### 🎯 Workflows Disponibles

#### 1. **Backend CI/CD** (`.github/workflows/backend-ci-cd.yml`)
- **Trigger**: Push o PR a `backend/**`
- **Acciones**:
  - Construye imagen Docker del backend
  - Push a Google Artifact Registry (con retry automático)
  - Actualiza **solo** el deployment del backend en el stack `gcp-deploy`
  - Ejecuta health checks automáticos
- **Tiempo estimado**: 3-5 minutos

#### 2. **Frontend CI/CD** (`.github/workflows/frontend-ci-cd.yml`)
- **Trigger**: Push o PR a `frontend/**`
- **Acciones**:
  - Construye imagen Docker del frontend
  - Push a Google Artifact Registry (con retry automático)
  - Actualiza **solo** el deployment del frontend en el stack `gcp-deploy`
  - Obtiene URL pública automáticamente
- **Tiempo estimado**: 3-5 minutos

#### 3. **Infrastructure CI/CD** (`.github/workflows/infrastructure-ci-cd.yml`)
- **Trigger**: Push o PR a `infrastructure-gcp-*/**`
- **Acciones**:
  - **Detección automática**: Identifica qué stack cambió (base/db/deploy)
  - **Deploy condicional**: Solo despliega el stack modificado
  - **Dependencias**: Si cambia `gcp-base`, redespliega `gcp-deploy` automáticamente
  - **Ejecución manual**: Disponible via `workflow_dispatch` con dropdown
- **Tiempo estimado**: 5-15 minutos (según stack)

#### 4. **Load Testing** (`.github/workflows/load-test.yml`)
- **Trigger**: Manual via `workflow_dispatch`
- **Acciones**:
  - Ejecuta pruebas de carga contra el cluster GKE
  - Monitorea métricas de autoscaling (HPA, pods, nodos)
  - Genera reporte detallado con resultados
- **Parámetros configurables**:
  - `target_url`: URL del frontend (auto-detecta si se omite)
  - `duration_seconds`: Duración de la prueba (default: 600s)
  - `workers`: Número de workers (default: 8)
  - `concurrent_per_worker`: Peticiones concurrentes (default: 150)

### 🔐 Configuración de Secretos

Para usar los workflows de CI/CD, debes configurar **3 secretos** en tu repositorio de GitHub:

1. **`GCP_SA_KEY`** - JSON de service account de GCP
2. **`PULUMI_ACCESS_TOKEN`** - Token de acceso a Pulumi Cloud
3. **`DB_ADMIN_PASSWORD`** - Password de PostgreSQL en Cloud SQL

📖 **Guía completa**: Ver [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md) para instrucciones detalladas paso a paso.

### 🚀 Cómo Usar

#### Despliegue Automático de Backend

```bash
# 1. Haz cambios en el backend
vim backend/app.py

# 2. Commit y push
git add backend/
git commit -m "feat: Add new API endpoint"
git push

# 3. El workflow backend-ci-cd.yml se ejecuta automáticamente
# - Construye nueva imagen Docker
# - Push a Artifact Registry
# - Actualiza deployment en GKE
# - Ejecuta health check
```

#### Despliegue Automático de Frontend

```bash
# 1. Haz cambios en el frontend
vim frontend/src/App.jsx

# 2. Commit y push
git add frontend/
git commit -m "feat: Update UI design"
git push

# 3. El workflow frontend-ci-cd.yml se ejecuta automáticamente
# - Construye nueva imagen Docker
# - Push a Artifact Registry
# - Actualiza deployment en GKE
# - Verifica URL pública
```

#### Despliegue Manual de Infraestructura

```bash
# Opción 1: Via código (trigger automático)
vim infrastructure-gcp-base/__main__.py
git add infrastructure-gcp-base/
git commit -m "chore: Update node pool config"
git push

# Opción 2: Via GitHub UI (manual)
# 1. Ve a Actions → Infrastructure CI/CD
# 2. Click "Run workflow"
# 3. Selecciona stack: base/db/deploy/all
# 4. Click "Run workflow"
```

#### Ejecutar Load Test

```bash
# Via GitHub UI:
# 1. Ve a Actions → GKE Autoscaling Load Test
# 2. Click "Run workflow"
# 3. Configura parámetros (o deja defaults)
# 4. Click "Run workflow"
# 5. Monitorea progreso en tiempo real
# 6. Revisa reporte en el summary del job
```

### 🛡️ Features de Seguridad y Confiabilidad

#### Retry Logic para Docker Push
```yaml
# Reintentos automáticos con backoff exponencial
- Intento 1: Push directo
- Intento 2: Espera 10s y reintenta
- Intento 3: Espera 20s y reintenta
- Intento 4: Espera 40s y reintenta
```

#### Manejo de Cluster Unreachable
```yaml
# Limpieza automática de recursos huérfanos
env:
  PULUMI_K8S_DELETE_UNREACHABLE: "true"
```

#### Health Checks Automáticos
```yaml
# Backend: Port-forward + curl
- kubectl port-forward → http://localhost:5000/health
# Frontend: LoadBalancer + curl
- curl http://<EXTERNAL-IP>/health
```

### 📊 Monitoreo de Workflows

Los workflows generan **summaries detallados** con información útil:

- **Backend/Frontend CI/CD**:
  - Image URL en Artifact Registry
  - Número de réplicas (actual vs deseadas)
  - Status de deployment
  - Comandos para monitoreo manual

- **Infrastructure CI/CD**:
  - Stack desplegado
  - Cluster endpoints
  - Frontend URL pública
  - Comandos kubectl de verificación

- **Load Test**:
  - Estado inicial del cluster (nodos, pods, HPAs)
  - Estado post-carga (escalado observado)
  - Eventos de scaling recientes
  - Utilización de recursos (CPU/Memoria)
  - Summary con verificación de criterios

### 🎯 Ejemplo de Flujo Completo

```bash
# Escenario: Añadir nuevo endpoint al backend

# 1. Crear rama de feature
git checkout -b feature/new-endpoint

# 2. Desarrollar cambios
vim backend/app.py
# ... código ...

# 3. Commit y push
git add backend/app.py
git commit -m "feat: Add /api/statistics endpoint"
git push origin feature/new-endpoint

# 4. Crear Pull Request en GitHub
# - El workflow backend-ci-cd.yml se ejecuta automáticamente
# - Verifica que la build es exitosa
# - Verifica que el deployment funciona

# 5. Merge a main
# - El workflow se ejecuta nuevamente
# - Despliega a producción automáticamente
# - Sistema actualizado en 3-5 minutos ✅
```

### 🔧 Troubleshooting de CI/CD

Ver [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md) sección "Troubleshooting" para errores comunes y soluciones.

---

## �📚 Documentación Adicional

- [ARQUITECTURA-K8S.md](./ARQUITECTURA-K8S.md) - Arquitectura detallada
- [GITHUB-ACTIONS-SETUP.md](./GITHUB-ACTIONS-SETUP.md) - Setup de secretos para CI/CD
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
