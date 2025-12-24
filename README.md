# Sistema de Autoscaling con Kubernetes (GKE / AKS)

Sistema de demostración de autoscaling automático desplegado en Google Kubernetes Engine (GKE) o Azure Kubernetes Service (AKS) con infraestructura como código usando Pulumi.


Este proyecto implementa una arquitectura **Micro-Stack** basada en los principios del libro **"Infrastructure as Code: Dynamic Systems for the Cloud Age"** de Kief Morris.


## Principios de IaC Implementados

### Capítulo 1: Mentalidad de la Edad de Nube
- **Velocidad + Calidad**: Infraestructura reproducible = cambios rápidos y seguros  
- **4 Métricas DORA**: Sistema preparado para CD (despliegues frecuentes, MTTR bajo)  
- **Piezas pequeñas débilmente acopladas**: Frontend, backend y DB independientes

### Capítulo 2: Principios de Infraestructura
- **Asumir sistemas no confiables**: Pods efímeros con health checks y auto-healing  
- **Hacer todo reproducible**: Toda la infraestructura definida como código  
- **Cosas desechables (Ganado no Mascotas)**: Pods reemplazables automáticamente  
- **Minimizar variación**: Node pools homogéneos, todas las VMs son iguales

### Capítulo 3: Plataformas de Infraestructura
- **Modelo 3 capas**:
  - **IaaS**: AKS cluster, VNET, NSG (infrastructure-k8s-base)
  - **PaaS**: PostgreSQL, Node pools (infrastructure-k8s-db)
  - **Aplicaciones**: Frontend/Backend pods (infrastructure-k8s-deploy)

### Capítulo 4: Define Todo como Código
- **Todo en VCS**: Git como fuente de verdad, todo versionado  
- **Declarativo**: Pulumi + Kubernetes manifiestos (idempotentes)  
- **GPL sobre DSL**: Pulumi con Python (no HCL/YAML puro)

### Capítulo 5: Micro-Stack Pattern
- **3 Pilas Independientes**:
  1. **k8s-base**: Infraestructura base (cluster AKS)
  2. **k8s-db**: Base de datos (ciclo de vida separado)
  3. **k8s-deploy**: Aplicaciones (frontend + backend)
- **Radio de explosión limitado**: Cambios aislados por pila  
- **Ciclos de vida independientes**: Puedo reconstruir el cluster sin tocar la DB

## Estructura del Proyecto

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

## Despliegue Completo

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

**Tiempo total**: 35-40 minutos

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

## Verificación

**IMPORTANTE**: `kubectl` solo se usa para **observar** lo que Pulumi creó. Todo se ejecuta desde tu equipo local.

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

## Autoscaling

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

## Pruebas de Carga

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
---

## Destruir Infraestructura

**Importante**: Destruir en orden inverso al despliegue.

**Para GCP** (automatizado):
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

## CI/CD con GitHub Actions

Este proyecto incluye workflows automatizados de CI/CD que despliegan automáticamente los cambios siguiendo el patrón **Micro-Stacks**.

### Workflows Disponibles

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

### Configuración de Secretos

Para usar los workflows de CI/CD, debes configurar **3 secretos** en tu repositorio de GitHub:

1. **`GCP_SA_KEY`** - JSON de service account de GCP
2. **`PULUMI_ACCESS_TOKEN`** - Token de acceso a Pulumi Cloud
3. **`DB_ADMIN_PASSWORD`** - Password de PostgreSQL en Cloud SQL


### Cómo Usar

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



## Licencia

Este proyecto está licenciado bajo la Licencia MIT.