# Arquitectura Kubernetes con AKS - Sistema Autoscaling

## 📐 Diseño basado en "Infrastructure as Code: Dynamic Systems for the Cloud Age"

### Principios IaC Aplicados

#### 1. **Micro-Stack Pattern** (Capítulo 5)
Separamos la infraestructura en pilas independientes con ciclos de vida propios:
- **infrastructure-k8s-base/**: Cluster AKS, red, seguridad (IaaS layer)
- **infrastructure-k8s-db/**: Base de datos PostgreSQL (datos persistentes)
- **infrastructure-k8s-deploy/**: Despliegue de aplicaciones (PaaS layer)

**Beneficio**: Puedo reconstruir el cluster sin tocar la base de datos. Radio de explosión limitado.

#### 2. **Define Todo como Código** (Capítulo 4)
- Toda la infraestructura en archivos de texto versionados
- Pulumi + Python (GPL) para infraestructura Azure
- Manifiestos YAML de Kubernetes para aplicaciones
- Git como fuente de verdad

#### 3. **Hacer Todo Reproducible** (Capítulo 2)
- Cada pila es idempotente
- Puedo destruir y reconstruir cualquier componente
- Documentación = código

#### 4. **Crear Cosas Desechables - Ganado no Mascotas** (Capítulo 2)
- Pods y nodos son reemplazables
- Node pools escalables automáticamente
- Sin configuración manual

#### 5. **Minimizar Variación** (Capítulo 2)
- Todas las VMs del cluster usan la misma imagen
- Node pools homogéneos
- Configuración centralizada

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                          AZURE CLOUD                             │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              AKS CLUSTER (infrastructure-k8s-base)        │  │
│  │                                                           │  │
│  │  ┌──────────────────┐        ┌──────────────────┐       │  │
│  │  │  Frontend Pool   │        │   Backend Pool   │       │  │
│  │  │  (Standard_B2s)  │        │  (Standard_B2s)  │       │  │
│  │  │  Min: 1, Max: 3  │        │  Min: 1, Max: 5  │       │  │
│  │  │                  │        │                  │       │  │
│  │  │  ┌────────────┐  │        │  ┌────────────┐  │       │  │
│  │  │  │ Frontend   │  │        │  │  Backend   │  │       │  │
│  │  │  │   Pods     │  │        │  │   Pods     │  │       │  │
│  │  │  │  (HPA)     │  │        │  │  (HPA)     │  │       │  │
│  │  │  └────────────┘  │        │  └────────────┘  │       │  │
│  │  └──────────────────┘        └──────────────────┘       │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────┐        │  │
│  │  │         Monitoring (System Pool)             │        │  │
│  │  │   Prometheus + Grafana                       │        │  │
│  │  └──────────────────────────────────────────────┘        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │   Azure Database for PostgreSQL Flexible Server          │  │
│  │   (infrastructure-k8s-db - Pila independiente)           │  │
│  │   Tier: Burstable B1ms                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │   Load Balancer (Ingress)                                │  │
│  │   HTTP: 80 → Frontend / API: 80/api → Backend            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Estructura del Proyecto

```
sistema-autoscaling/
├── infrastructure-k8s-base/         # Pila 1: Infraestructura base (IaaS)
│   ├── __main__.py                  # AKS cluster, VNET, NSG, node pools
│   ├── Pulumi.yaml
│   ├── Pulumi.production.yaml
│   └── requirements.txt
│
├── infrastructure-k8s-db/           # Pila 2: Base de datos (Micro-stack)
│   ├── __main__.py                  # PostgreSQL Flexible Server
│   ├── Pulumi.yaml
│   ├── Pulumi.production.yaml
│   └── requirements.txt
│
├── infrastructure-k8s-deploy/       # Pila 3: Despliegue K8s (PaaS)
│   ├── __main__.py                  # Aplica manifiestos K8s con Pulumi
│   ├── Pulumi.yaml
│   ├── Pulumi.production.yaml
│   └── requirements.txt
│
├── k8s/                             # Manifiestos Kubernetes
│   ├── backend/
│   │   ├── deployment.yaml          # Backend deployment + HPA
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── frontend/
│   │   ├── deployment.yaml          # Frontend deployment + HPA
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   └── ingress.yaml
│   └── monitoring/
│       ├── prometheus.yaml
│       ├── grafana.yaml
│       └── servicemonitor.yaml
│
├── backend/                         # Código de la aplicación
├── frontend/
└── scripts/
```

---

## 🔧 Componentes

### 1. AKS Cluster (infrastructure-k8s-base)
- **Node Pools**:
  - `systempool`: 1 nodo Standard_B2s (sistema, monitoreo)
  - `frontend`: 1-3 nodos Standard_B2s (autoscaling)
  - `backend`: 1-5 nodos Standard_B2s (autoscaling)
- **Networking**: Azure CNI
- **Free Tier**: AKS control plane gratis

### 2. Azure Database for PostgreSQL (infrastructure-k8s-db)
- **Tier**: Burstable B1ms (1 vCore, 2 GiB RAM)
- **Storage**: 32 GiB
- **Pila separada**: Permite actualizar cluster sin tocar datos

### 3. Backend (Flask)
- **Deployment**: 2-10 réplicas
- **HPA**: Escala en CPU >70% y Memoria >80%
- **Node Affinity**: Solo en node pool backend
- **Health Checks**: /health endpoint

### 4. Frontend (React + Nginx)
- **Deployment**: 1-5 réplicas
- **HPA**: Escala en CPU >60%
- **Node Affinity**: Solo en node pool frontend
- **Ingress**: Rutas / y /api

### 5. Observabilidad
- **Prometheus**: Métricas de pods, nodos, aplicaciones
- **Grafana**: Dashboards de performance
- **Service Monitors**: Scraping automático

---

## 🚀 Proceso de Despliegue

### Orden de despliegue (respetando dependencias):

```bash
# 1. Pila base (AKS cluster)
cd infrastructure-k8s-base
pulumi up

# 2. Pila de base de datos (independiente)
cd ../infrastructure-k8s-db
pulumi up

# 3. Pila de despliegue (aplicaciones K8s)
cd ../infrastructure-k8s-deploy
pulumi up
```

---

## 🎯 Conceptos IaC del Libro Implementados

### Capítulo 1: Mentalidad de la Edad de Nube
✅ **Velocidad + Calidad**: Infraestructura reproducible permite cambios rápidos seguros
✅ **4 Métricas DORA**: Preparado para CD (despliegues frecuentes, MTTR bajo)

### Capítulo 2: Principios de Infraestructura
✅ **Asumir sistemas no confiables**: Pods y nodos son efímeros
✅ **Hacer reproducible**: Todo definido como código
✅ **Cosas desechables**: Ganado no mascotas (pods reemplazables)
✅ **Minimizar variación**: Node pools homogéneos

### Capítulo 3: Plataformas de Infraestructura
✅ **Modelo 3 capas**:
  - IaaS: AKS, VNET, NSG (infrastructure-k8s-base)
  - PaaS: PostgreSQL, node pools (infrastructure-k8s-db)
  - Aplicaciones: Frontend/Backend pods (infrastructure-k8s-deploy)

### Capítulo 4: Define Todo como Código
✅ **Todo en VCS**: Git como fuente de verdad
✅ **Declarativo**: Pulumi + K8s manifiestos
✅ **Idempotente**: pulumi up ejecutable múltiples veces

### Capítulo 5: Pilas de Infraestructura
✅ **Micro-Stack Pattern**: 3 pilas independientes
✅ **Radio de explosión limitado**: Cambios aislados por pila
✅ **Ciclos de vida separados**: DB separada del cluster

---

## 💰 Costos Estimados (Free Tier Azure)

- AKS Control Plane: **$0** (gratis)
- Node Pool System (1x B2s): ~$30/mes
- Node Pool Frontend (1-3x B2s): ~$30-90/mes
- Node Pool Backend (1-5x B2s): ~$30-150/mes
- PostgreSQL B1ms: ~$12/mes
- Load Balancer: ~$20/mes

**Total estimado**: $92-302/mes (dependiendo del autoscaling)

---

## 📊 Autoscaling

### Horizontal Pod Autoscaler (HPA)
- **Backend**: 2-10 réplicas, CPU 70%, RAM 80%
- **Frontend**: 1-5 réplicas, CPU 60%

### Cluster Autoscaler
- **Frontend pool**: 1-3 nodos
- **Backend pool**: 1-5 nodos
- **System pool**: 1 nodo fijo

---

## 🔒 Seguridad

- Network Security Groups (NSG)
- Azure CNI con network policies
- Secretos en Pulumi Secrets
- PostgreSQL solo accesible desde AKS
- Ingress con reglas de routing

---

## 📈 Próximos Pasos

1. ✅ Estructura de directorios
2. ⏳ Crear pila infrastructure-k8s-base
3. ⏳ Crear pila infrastructure-k8s-db
4. ⏳ Crear manifiestos Kubernetes
5. ⏳ Crear pila infrastructure-k8s-deploy
6. ⏳ Configurar monitoreo
7. ⏳ Documentar comandos de despliegue
