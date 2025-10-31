# Frontend Kubernetes Manifests

## 📋 Descripción
Manifiestos de Kubernetes para el frontend React + Nginx con autoscaling.

## 🎯 Principios IaC Aplicados
- **Ganado no Mascotas** (Cap 2): Pods desechables y reemplazables
- **Asumir sistemas no confiables** (Cap 2): Health checks y auto-healing
- **Minimizar variación** (Cap 2): Node affinity para pool específico
- **Piezas pequeñas débilmente acopladas** (Cap 1): Frontend independiente

## 📦 Recursos Incluidos
- **Namespace**: frontend
- **ConfigMap**: nginx-config (configuración de Nginx con proxy a backend)
- **Deployment**: 1-5 réplicas con node affinity
- **Service**: LoadBalancer público para acceso desde internet
- **HPA**: Autoscaling basado en CPU (60%) y Memoria (70%)

## 🚀 Características

### Nginx Configuration
- **SPA Routing**: Maneja rutas de React correctamente
- **API Proxy**: `/api/*` → `backend-service.backend.svc.cluster.local`
- **Health Check**: `/health` endpoint para probes

### Node Affinity
Los pods solo se despliegan en nodos con label `workload=frontend`.

### LoadBalancer
El Service usa tipo `LoadBalancer` para obtener una IP pública de Azure.

### Autoscaling
- **Min**: 1 réplica
- **Max**: 5 réplicas
- **CPU**: Escala en 60%
- **Memoria**: Escala en 70%
- **Scale Up**: Espera 30s (conservador)
- **Scale Down**: Espera 5 min (muy conservador)

## 📊 Recursos por Pod
- **Requests**: 50m CPU, 64Mi RAM
- **Limits**: 200m CPU, 256Mi RAM

## 🌐 Acceso
Una vez desplegado, obtén la IP pública:
```bash
kubectl get svc -n frontend frontend-service
```

Accede a la aplicación:
```
http://<EXTERNAL-IP>/
```

## 🔧 Variables a Configurar
Antes de desplegar, reemplazar:
- `DOCKER_IMAGE_PLACEHOLDER` con tu imagen Docker del frontend

## 🔗 Endpoints
- `/` - Aplicación React
- `/api/*` - Proxy a backend
- `/health` - Health check
