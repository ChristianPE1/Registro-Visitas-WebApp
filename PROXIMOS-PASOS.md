# 🎯 Próximos Pasos para Desplegar el Proyecto

## ✅ Completado
1. ✅ Deshabilitado workflow automático de GitHub Actions
2. ✅ Diseñada arquitectura Kubernetes con patrón Micro-Stack
3. ✅ Creadas 3 pilas de Pulumi independientes (base, db, deploy)
4. ✅ Creados manifiestos de Kubernetes para backend y frontend
5. ✅ Configurado sistema de monitoreo (Prometheus + Grafana)
6. ✅ Documentada arquitectura completa y conceptos IaC

## 📋 Checklist de Despliegue

### Antes de Empezar
- [ ] Tener cuenta de Azure activa (Free Tier funciona)
- [ ] Instalar Azure CLI: `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`
- [ ] Login a Azure: `az login`
- [ ] Instalar Pulumi: `curl -fsSL https://get.pulumi.com | sh`
- [ ] Instalar kubectl: `az aks install-cli`
- [ ] Tener Docker instalado

### Paso 1: Desplegar Cluster AKS (15 min)
```bash
cd infrastructure-k8s-base
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pulumi login
pulumi stack init production

# Generar SSH key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aks_key
pulumi config set ssh_public_key "$(cat ~/.ssh/aks_key.pub)"

# Desplegar
pulumi up
```

### Paso 2: Desplegar Base de Datos (10 min)
```bash
cd ../infrastructure-k8s-db
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pulumi stack init production

# Configurar password seguro
pulumi config set --secret db_admin_password "TuPasswordSegura123!"

# Desplegar
pulumi up
```

### Paso 3: Construir Imágenes Docker (10 min)
```bash
# Crear Azure Container Registry
az acr create --resource-group cpe-k8s-autoscaling-rg \
  --name cpeautoscalingacr --sku Basic

# Login
az acr login --name cpeautoscalingacr

# Backend
cd backend
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-backend:v1 .
docker push cpeautoscalingacr.azurecr.io/autoscaling-backend:v1

# Frontend
cd ../frontend
docker build -t cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1 .
docker push cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1

# Dar permisos a AKS
az aks update --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks \
  --attach-acr cpeautoscalingacr
```

### Paso 4: Desplegar Aplicaciones (5 min)
```bash
cd ../infrastructure-k8s-deploy
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Obtener kubeconfig
az aks get-credentials --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks --overwrite-existing

# Configurar
pulumi stack init production
pulumi config set backend_image cpeautoscalingacr.azurecr.io/autoscaling-backend:v1
pulumi config set frontend_image cpeautoscalingacr.azurecr.io/autoscaling-frontend:v1
pulumi config set --secret db_admin_password "TuPasswordSegura123!"

# Desplegar
pulumi up
```

### Paso 5: Desplegar Monitoreo (2 min)

**IMPORTANTE**: El monitoreo también debe ser IaC. Por ahora, si quieres verlo funcionando:

```bash
# Opción A: Aplicar manualmente (temporal, para demo)
kubectl apply -f k8s/monitoring/prometheus-grafana.yaml

# Opción B: Crear una Pila 4 de Pulumi (recomendado para producción)
# TODO: Migrar monitoring a Pulumi también
```

### Verificar Despliegue (Solo Observación)

**IMPORTANTE**: `kubectl` solo se usa para **VER** lo que Pulumi creó, NO para crear recursos.

```bash
# Ver todos los pods creados POR PULUMI
kubectl get pods --all-namespaces

# Ver servicios e IPs públicas creadas POR PULUMI
kubectl get svc --all-namespaces

# Ver HPA creados POR PULUMI
kubectl get hpa -n backend
kubectl get hpa -n frontend

# Obtener URL del frontend (desde Pulumi, mejor opción)
cd infrastructure-k8s-deploy
pulumi stack output frontend_url
```

## 🎓 Conceptos IaC Aplicados

### Del Libro "Infrastructure as Code" (Kief Morris)

1. **Micro-Stack Pattern** (Cap 5)
   - 3 pilas independientes con ciclos de vida propios
   - Radio de explosión limitado por pila
   - Puedo destruir cluster sin afectar DB

2. **Define Todo como Código** (Cap 4)
   - Todo en Git, versionado
   - Pulumi con Python (GPL, no DSL)
   - Manifiestos declarativos de Kubernetes

3. **Hacer Todo Reproducible** (Cap 2)
   - Infraestructura idempotente
   - Puedo reconstruir cualquier componente
   - Sin "copos de nieve"

4. **Ganado no Mascotas** (Cap 2)
   - Pods desechables y reemplazables
   - Node pools escalables
   - Sin configuración manual

5. **Minimizar Variación** (Cap 2)
   - Node pools homogéneos
   - Todas las VMs son iguales
   - Configuración centralizada

## 🔍 Comandos Útiles

### Monitoreo en Tiempo Real
```bash
# Ver HPA del backend
watch kubectl get hpa -n backend

# Ver pods del backend
watch kubectl get pods -n backend

# Ver nodos del cluster
watch kubectl get nodes

# Métricas de recursos
kubectl top nodes
kubectl top pods -n backend
```

### Logs
```bash
# Backend logs
kubectl logs -n backend -l app=backend --tail=50 -f

# Frontend logs
kubectl logs -n frontend -l app=frontend --tail=50 -f
```

### Pruebas de Carga
```bash
# Desde la interfaz web
# Abrir http://<FRONTEND-IP> y usar botones de prueba

# Desde scripts
cd scripts
python3 extreme-load.py --url http://<FRONTEND-IP> --duration 300
```

## ⚠️ Notas Importantes

1. **SSH Key**: Necesitas generar una SSH key antes del Paso 1
2. **Passwords**: Usa el mismo password en Paso 2 y Paso 4
3. **ACR Name**: `cpeautoscalingacr` debe ser único globalmente en Azure
4. **Costos**: El proyecto costará ~$90-300/mes según autoscaling
5. **Free Tier**: AKS control plane es gratis, solo pagas por nodos
6. **Orden de destrucción**: Inverso al despliegue (deploy → db → base)

## 📚 Documentación de Referencia

- `ARQUITECTURA-K8S.md` - Arquitectura completa detallada
- `infrastructure-k8s-base/README.md` - Pila 1 (Cluster)
- `infrastructure-k8s-db/README.md` - Pila 2 (Database)
- `infrastructure-k8s-deploy/README.md` - Pila 3 (Apps)
- `k8s/backend/README.md` - Manifiestos backend
- `k8s/frontend/README.md` - Manifiestos frontend
- `k8s/monitoring/README.md` - Prometheus + Grafana

## 🚀 ¡Éxito en tu Despliegue!

Si encuentras algún problema:
1. Revisa los logs de Pulumi
2. Verifica que todos los pre-requisitos estén instalados
3. Asegúrate de estar en el directorio correcto
4. Verifica que el entorno virtual esté activado

**¡El sistema está listo para ser desplegado!** 🎉
