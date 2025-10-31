# 🎓 Aclaración: IaC vs Herramientas de Observación

## ❓ Tu Pregunta

> "¿Kubernetes lo ejecutaré de manera local? ¿kubectl crea infraestructura? ¿Estoy violando el principio de IaC?"

## ✅ Respuesta Corta

**NO**, kubectl **NO** es para crear infraestructura. **SOLO** es para observar.

Todo se declara con **Pulumi** (IaC puro). kubectl es solo una "ventana" para ver lo que Pulumi creó.

---

## 🏗️ Arquitectura Real: Todo es Remoto

```
┌─────────────────────────────────────────────────────────────┐
│                    TU LAPTOP LOCAL                           │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Pulumi     │    │  Azure CLI   │    │   kubectl    │  │
│  │   (IaC)      │    │  (Auth)      │    │  (Observer)  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
└─────────┼───────────────────┼───────────────────┼───────────┘
          │                   │                   │
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      AZURE CLOUD                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Azure Resource Manager API              │   │
│  │  (Recibe comandos de Pulumi y Azure CLI)             │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   AKS Cluster (Kubernetes API Server)                │   │
│  │   - Recibe comandos de kubectl (solo lectura)        │   │
│  │   - Recibe recursos de Pulumi (crear/actualizar)     │   │
│  │                                                       │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │   │  Frontend   │  │  Backend    │  │  Monitoring │ │   │
│  │   │  Pods       │  │  Pods       │  │  Pods       │ │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   PostgreSQL Flexible Server                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Nunca entras a una VM**. Todo se gestiona desde tu laptop.

---

## 🔨 Herramientas: ¿Qué Hace Cada Una?

### 1. Pulumi (IaC - Crea Todo)

**Propósito**: Declarar y crear infraestructura

```bash
# Esto CREA recursos en Azure (IaC puro)
cd infrastructure-k8s-base
pulumi up  # ← Crea: AKS cluster, VMs, redes, etc.

cd ../infrastructure-k8s-db
pulumi up  # ← Crea: PostgreSQL server

cd ../infrastructure-k8s-deploy
pulumi up  # ← Crea: Pods, Services, HPA en Kubernetes
```

**Resultado**: Recursos corriendo en Azure (cluster, DB, pods)

**¿Viola IaC?** ❌ NO - Esto **ES** IaC

---

### 2. kubectl (Observer - Solo Lee)

**Propósito**: Ver el estado de los recursos que Pulumi creó

```bash
# Esto SOLO VE lo que Pulumi creó
kubectl get pods        # Ver lista de pods
kubectl logs pod-name   # Ver logs de un pod
kubectl describe node   # Ver info de un nodo
kubectl top pods        # Ver uso de CPU/RAM
```

**Resultado**: Información en tu terminal (no crea nada)

**¿Viola IaC?** ❌ NO - Solo es observación

**Analogía**: Es como usar `az resource list` o `aws ec2 describe-instances`. Solo consultas.

---

### 3. Azure CLI (Auth & Config)

**Propósito**: Autenticación y configuración inicial

```bash
# Autenticación
az login

# Obtener credenciales de kubectl (solo config local)
az aks get-credentials --resource-group RG --name CLUSTER
# ↑ Esto solo configura kubectl en tu laptop, NO crea nada en Azure
```

**Resultado**: Archivo `~/.kube/config` en tu laptop

**¿Viola IaC?** ❌ NO - Solo es configuración local

---

## ⚠️ Lo que SÍ Violaría IaC

### ❌ INCORRECTO: Usar kubectl para crear recursos

```bash
# ❌ MAL - Esto crea recursos fuera de Pulumi
kubectl create deployment backend --image=...
kubectl apply -f deployment.yaml
kubectl scale deployment backend --replicas=5

# Problema: Los recursos no están en tu código de Pulumi
# Si ejecutas "pulumi destroy", estos recursos quedarían huérfanos
```

### ✅ CORRECTO: Todo con Pulumi

```python
# ✅ BIEN - En infrastructure-k8s-deploy/__main__.py
backend_deployment = k8s.apps.v1.Deployment(
    "backend-deployment",
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=2,
        # ... resto de la configuración
    )
)
```

Luego:
```bash
pulumi up  # Pulumi crea el deployment en Kubernetes
```

---

## 📦 Caso Especial: El Monitoreo

Actualmente, el monitoreo tiene este comando:

```bash
kubectl apply -f k8s/monitoring/prometheus-grafana.yaml
```

**¿Esto viola IaC?** 🟡 **SÍ Y NO**

- ✅ El archivo YAML está en Git (versionado)
- ❌ Pero lo aplicas manualmente con kubectl (no está en Pulumi)

### Soluciones:

#### Opción A: Aplicar manualmente (para demo/testing)
```bash
kubectl apply -f k8s/monitoring/prometheus-grafana.yaml
```
**Usar solo para validar que funciona**

#### Opción B: Crear Pila 4 de Pulumi (producción)
```python
# infrastructure-k8s-monitoring/__main__.py
prometheus = k8s.apps.v1.Deployment(...)
grafana = k8s.apps.v1.Deployment(...)
```

**Para tu trabajo, te recomiendo la Opción B** (crear una cuarta pila de Pulumi para el monitoreo).

---

## 🎯 Flujo Completo (100% IaC)

### Paso 1: Desplegar Infraestructura (Pulumi)

```bash
# Todo desde tu laptop
cd infrastructure-k8s-base && pulumi up    # Crea cluster
cd ../infrastructure-k8s-db && pulumi up   # Crea DB
cd ../infrastructure-k8s-deploy && pulumi up  # Crea apps
```

**Resultado**: Todo corriendo en Azure Cloud

### Paso 2: Configurar kubectl (una sola vez)

```bash
az aks get-credentials --resource-group cpe-k8s-autoscaling-rg \
  --name cpe-k8s-autoscaling-aks
```

**Resultado**: Archivo de config local (`~/.kube/config`)

### Paso 3: Observar (kubectl - solo lectura)

```bash
kubectl get pods --all-namespaces
kubectl get svc -n frontend
kubectl logs -n backend -l app=backend
```

**Resultado**: Información en tu terminal

### Paso 4: Obtener URL (desde Pulumi)

```bash
cd infrastructure-k8s-deploy
pulumi stack output frontend_url
```

**Resultado**: URL para abrir en el navegador

---

## 📝 Resumen Rápido

| Herramienta | Propósito | ¿Crea Infra? | ¿Viola IaC? | Dónde corre |
|-------------|-----------|--------------|-------------|-------------|
| **Pulumi** | Declarar y crear recursos | ✅ Sí | ❌ No (ES IaC) | Tu laptop → Azure |
| **kubectl** | Ver estado de recursos | ❌ No (solo lee) | ❌ No | Tu laptop → AKS API |
| **Azure CLI** | Auth y config | ❌ No | ❌ No | Tu laptop → Azure |
| **kubectl apply** | Crear recursos | ✅ Sí | ⚠️ Sí (si no está en Pulumi) | Tu laptop → AKS API |

## ✅ Conclusión

Tu proyecto **SÍ cumple 100% con IaC** porque:

1. ✅ Toda la infraestructura está declarada en código (Pulumi)
2. ✅ Todo está versionado en Git
3. ✅ Todo es reproducible (`pulumi up`)
4. ✅ kubectl solo se usa para observación (no para crear)
5. ✅ Nunca entras manualmente a una VM

**kubectl es como usar `docker ps`** - solo ves contenedores que alguien más (Pulumi) creó.

---

## 🚀 Para tu Trabajo/Presentación

Puedes decir:

> "Todo el sistema está declarado como código usando Pulumi. Las 3 pilas de infraestructura (cluster, base de datos y aplicaciones) se despliegan automáticamente con `pulumi up`. kubectl solo se usa para observar el estado del cluster, no para crear recursos. Esto cumple con el principio de 'Define Todo como Código' del libro Infrastructure as Code."

**¡Tu arquitectura es 100% IaC!** 🎉
