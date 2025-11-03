# Pila 3: Despliegue de Aplicaciones en Kubernetes

## 📋 Descripción
Despliega el backend y frontend en AKS usando Pulumi con Kubernetes provider.

## 🎯 Principios IaC Aplicados
- **Probar y entregar continuamente** (Cap 4): Despliegue automatizado
- **Define todo como código** (Cap 4): Manifiestos programáticos
- **Piezas pequeñas débilmente acopladas** (Cap 1): Backend y frontend independientes
- **PaaS Layer** (Cap 3): Aplicaciones sobre infraestructura

## 📦 Recursos Creados
### Backend
- Namespace: `backend`
- Secret: Credenciales de base de datos
- ConfigMap: Variables de entorno
- Deployment: 2-10 réplicas con node affinity
- Service: ClusterIP
- HPA: Autoscaling CPU 70%, RAM 80%

### Frontend
- Namespace: `frontend`
- ConfigMap: Configuración de Nginx
- Deployment: 1-5 réplicas con node affinity
- Service: LoadBalancer (IP pública)
- HPA: Autoscaling CPU 60%

## 🚀 Despliegue

### Pre-requisitos
1. Haber desplegado Pila 1 (k8s-base)
2. Haber desplegado Pila 2 (k8s-db)
3. Tener imágenes Docker del backend y frontend publicadas en un registry

### Construir y publicar imágenes Docker

#### Opción 1: Azure Container Registry (ACR)
```bash
# Crear ACR
az acr create --resource-group cpe-k8s-autoscaling-rg \
  --name cpeautoscalingacr --sku Basic

# Login a ACR
az acr login --name cpeautoscalingacr

# Construir y push backend
cd backend
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-backend:v1 .
docker push cpeautoscalingacr.azurecr.io/autoscaling-backend:v1

# Construir y push frontend
cd ../frontend
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1 .
docker push cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1

# Dar permisos a AKS para pull desde ACR
az aks update --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks \
  --attach-acr cpeautoscalingacr
```

#### Opción 2: Docker Hub
```bash
# Login a Docker Hub
docker login

# Construir y push
docker build -t YOUR_USERNAME/autoscaling-backend:v1 ./backend
docker push YOUR_USERNAME/autoscaling-backend:v1

docker build -t YOUR_USERNAME/autoscaling-frontend:v1 ./frontend
docker push YOUR_USERNAME/autoscaling-frontend:v1
```

### Configurar Pulumi
```bash
cd infrastructure-k8s-deploy

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Seleccionar stack
pulumi stack select production

# Configurar imágenes Docker
pulumi config set backend_image cpeautoscalingacr.azurecr.io/autoscaling-backend:v1
pulumi config set frontend_image cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1

# Configurar password de DB (mismo que usaste en k8s-db)
pulumi config set --secret db_admin_password YOUR_DB_PASSWORD

# Obtener kubeconfig de AKS
az aks get-credentials --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks --overwrite-existing
```

### Desplegar
```bash
# Preview
pulumi preview

# Desplegar
pulumi up

# Ver outputs
pulumi stack output
```

## 🔍 Verificación
```bash
# Ver pods
kubectl get pods -n backend
kubectl get pods -n frontend

# Ver servicios
kubectl get svc -n backend
kubectl get svc -n frontend

# Ver HPA status
kubectl get hpa -n backend
kubectl get hpa -n frontend

# Logs del backend
kubectl logs -n backend -l app=backend --tail=50

# Logs del frontend
kubectl logs -n frontend -l app=frontend --tail=50
```

## 🌐 Acceso a la Aplicación
```bash
# Obtener IP pública del frontend
kubectl get svc -n frontend frontend-service

# O desde Pulumi
pulumi stack output frontend_url
```

Abre tu navegador en: `http://<FRONTEND-EXTERNAL-IP>`

## 🔄 Actualizar Aplicación
```bash
# Construir nueva versión
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-backend:v2 ./backend
docker push cpeautoscalingacr.azurecr.io/autoscaling-backend:v2

# Actualizar config de Pulumi
pulumi config set backend_image cpeautoscalingacr.azurecr.io/autoscaling-backend:v2

# Redesplegar (solo afectará backend)
pulumi up
```

## 📊 Monitoreo
Desplegar el stack de monitoreo:
```bash
kubectl apply -f k8s/monitoring/prometheus-grafana.yaml

# Obtener IP de Grafana
kubectl get svc -n monitoring grafana-service

# Acceder a Grafana
# http://<GRAFANA-IP>:3000
# Usuario: admin, Contraseña: admin
```

## 🗑️ Eliminar
```bash
# Eliminar aplicaciones
pulumi destroy

# Esto NO eliminará el cluster AKS ni la base de datos
# (están en pilas separadas - Micro-Stack Pattern)
```

## 🔗 Siguiente Paso
- Configurar dashboards en Grafana
- Ejecutar pruebas de carga para validar autoscaling
- Documentar métricas de las 4 DORA
