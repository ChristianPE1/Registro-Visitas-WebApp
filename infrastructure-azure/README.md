# Infrastructure as Code - Azure Implementation# Sistema de Autoscaling en Azure con Pulumi



## OverviewDemo de autoscaling horizontal usando Pulumi (IaC open source) en Azure



This directory contains the Infrastructure as Code (IaC) implementation using Pulumi to deploy an autoscaling web application on Microsoft Azure.## 🏗️ Arquitectura



## Architecture- **IaC**: Pulumi Python

- **Cloud**: Azure (región West US)

### System Components- **Backend**: Flask + PostgreSQL Flexible Server (B1ms)

- **Frontend**: React + Tailwind CSS (local)

```- **Compute**: VM Scale Set (Standard_B1s, 1-3 instancias)

┌─────────────────────────────────────────────┐- **Load Balancer**: Azure Load Balancer con health probes

│          Azure Cloud Infrastructure         │- **Database**: PostgreSQL Flexible Server 13 (Standard_B1ms, 32GB)

├─────────────────────────────────────────────┤- **Autoscaling**: Basado en CPU (>70% = scale up, <30% = scale down)

│                                             │

│  ┌───────────────────────────────────────┐ │## 📋 Requisitos

│  │      Public Load Balancer             │ │

│  │  Standard SKU with NAT Gateway        │ │- Python 3.13+

│  └──────────┬────────────────────────────┘ │- Pulumi CLI

│             │                               │- Azure CLI

│     ┌───────┴────────┬──────────────┐      │- Cuenta Azure con suscripción activa

│     │                │              │      │

│  ┌──▼───┐        ┌──▼───┐      ┌──▼───┐   │## 🚀 Deployment

│  │ VM 1 │        │ VM 2 │      │ VM 3 │   │

│  │ B1s  │        │ B1s  │      │ B1s  │   │### 1. Destruir infraestructura anterior (si existe)

│  └──┬───┘        └──┬───┘      └──┬───┘   │

│     │               │              │       │```bash

│     └───────────────┴──────────────┘       │cd infrastructure-azure

│                     │                      │pulumi destroy --yes

│           ┌─────────▼─────────┐            │```

│           │ PostgreSQL Flexible│            │

│           │     Server B1s     │            │### 2. Desplegar nueva infraestructura

│           └────────────────────┘            │

│                                             │```bash

└─────────────────────────────────────────────┘pulumi up --yes

``````



### Infrastructure Resources**Tiempo estimado**: 10-15 minutos



#### Network Layer### 3. Obtener outputs

- **Virtual Network**: 10.0.0.0/16

  - VM Subnet: 10.0.1.0/24```bash

  - Database Subnet: 10.0.2.0/24pulumi stack output

- **Network Security Group**: Controls inbound/outbound traffic```

  - HTTP (80), Flask (5000), SSH (22)

  - Grafana (3000), Prometheus (9090)Outputs importantes:

- **NAT Gateway**: Provides outbound internet connectivity- `load_balancer_ip`: IP pública del Load Balancer

- **Public Load Balancer**: Standard SKU- `load_balancer_url`: URL de la aplicación

  - Health probes for Flask, Grafana, Prometheus- `ssh_command`: Comando para conectar por SSH

  - Inbound NAT pool for SSH (ports 50000-50099)- `postgres_server`: FQDN del servidor PostgreSQL

- `health_endpoint`: Endpoint de health check

#### Compute Layer- `api_stress_endpoint`: Endpoint para generar carga

- **Virtual Machine Scale Set (VMSS)**

  - VM Size: Standard_B1s (1 vCPU, 1 GiB RAM)## 🔧 Características Implementadas

  - OS: Ubuntu 22.04 LTS

  - Capacity: 1-3 instances (autoscaling)### ✅ User Data Script Mejorado

  - Upgrade Policy: Manual

- **Systemd service**: Flask se ejecuta como servicio con auto-reinicio

#### Database Layer- **Logs detallados**: `/var/log/user-data.log` y `/var/log/flask-app.log`

- **PostgreSQL Flexible Server**- **Health checks**: Verifica que Flask esté corriendo antes de completar

  - SKU: Standard_B1s (1 vCore, 2 GiB RAM, 32 GB storage)- **Frontend**: Instala dependencias de React (opcional)

  - Version: 13- **Manejo de errores**: Script con `set -ex` para debugging

  - Firewall: Azure services allowed

### ✅ SSH Access vía NAT Pool

#### Monitoring Layer

Each VM instance includes:Las VMs son accesibles por SSH a través del Load Balancer:

- **Prometheus**: Metrics collection and storage (port 9090)

- **Grafana**: Metrics visualization (port 3000)```bash

- **Node Exporter**: System metrics (port 9100)# VM 0 (primera instancia)

- **Flask Prometheus Exporter**: Application metricsssh -p 50000 azureuser@<LOAD_BALANCER_IP>



### Application Stack# VM 1 (segunda instancia, si existe)

ssh -p 50001 azureuser@<LOAD_BALANCER_IP>

Each VMSS instance runs:

1. **Flask Backend** (Python 3, port 5000)# VM 2 (tercera instancia, si existe)

   - REST API for visits managementssh -p 50002 azureuser@<LOAD_BALANCER_IP>

   - PostgreSQL connection with fallback```

   - Prometheus metrics export

2. **Monitoring Services****Password**: `AzureAdmin2025!`

   - Prometheus server

   - Grafana dashboard### ✅ Boot Diagnostics Habilitado

   - Node exporter for system metrics

Los boot diagnostics están activos en el VMSS:

### Autoscaling Configuration

- Acceso a Serial Console en Azure Portal

**Scale-Out Rule:**- Logs de arranque disponibles

- Trigger: Average CPU > 70%- Troubleshooting mejorado

- Time Window: 5 minutes

- Action: Add 1 VM instance## 🧪 Testing

- Cooldown: 5 minutes

### Health Check

**Scale-In Rule:**

- Trigger: Average CPU < 30%```bash

- Time Window: 5 minutescurl http://<LOAD_BALANCER_IP>/health

- Action: Remove 1 VM instance```

- Cooldown: 5 minutes

Respuesta esperada:

**Limits:**```json

- Minimum: 1 instance{

- Maximum: 3 instances  "status": "healthy",

- Default: 1 instance  "database": "connected",

  "timestamp": "2025-10-25T..."

## Service Communication}

```

### Load Balancer Rules

### Stress Test Automatizado

| Frontend Port | Backend Port | Service | Protocol |

|--------------|--------------|---------|----------|```bash

| 80 | 5000 | Flask API | TCP |python3 test_autoscaling.py <LOAD_BALANCER_IP>

| 3000 | 3000 | Grafana | TCP |```

| 9090 | 9090 | Prometheus | TCP |

| 50000-50099 | 22 | SSH (NAT Pool) | TCP |Este script:

1. Verifica el health endpoint

### Data Flow2. Obtiene métricas iniciales

3. Genera carga CPU con 5 threads concurrentes (60s cada uno)

1. **Inbound Traffic**: Client → Load Balancer → VMSS instances (round-robin)4. Muestra métricas finales

2. **Database Access**: VMSS instances → PostgreSQL Flexible Server (private connection)5. Proporciona instrucciones de monitoreo

3. **Outbound Traffic**: VMSS instances → NAT Gateway → Internet

4. **Monitoring**: Prometheus (per instance) → Collects from Flask + Node Exporter### Debug Helper Interactivo

5. **Visualization**: Grafana → Queries local Prometheus

```bash

## Files./debug_helper.sh

```

- `__main__.py`: Main Pulumi infrastructure definition

- `Pulumi.yaml`: Project configurationMenú interactivo con opciones para:

- `Pulumi.production-azure.yaml`: Stack-specific settings1. SSH a cualquier VM

- `requirements.txt`: Python dependencies for Pulumi2. Verificar health endpoint

- `test_autoscaling.py`: Load test script for autoscaling validation3. Ver instancias del VMSS

- `check_deployment.sh`: Deployment verification script4. Ver métricas de CPU

5. Ejecutar stress test

## Deployment6. Ver logs via Azure CLI



### Prerequisites## 📊 Monitoreo de Autoscaling



- Azure CLI installed and authenticated### Vía Azure Portal

- Pulumi CLI installed

- Python 3.8+1. Ir a: **Virtual Machine Scale Sets** > `cpe-autoscaling-demo-vmss`

2. Click en **Instances** para ver número de VMs

### Configuration3. Click en **Metrics** para ver CPU percentage

4. Click en **Autoscale** para ver reglas activas

Set required secrets:

```bash### Vía Azure CLI

pulumi config set --secret admin_password <PASSWORD>

pulumi config set --secret db_password <PASSWORD>```bash

pulumi config set location westus# Ver instancias

```az vmss list-instances \

  -g cpe-autoscaling-demo-rg \

### Deploy Infrastructure  -n cpe-autoscaling-demo-vmss \

  --query '[].{Name:name, State:provisioningState, InstanceID:instanceId}' \

```bash  -o table

cd infrastructure-azure

pulumi up# Ver métricas CPU (últimos 30 min)

```az monitor metrics list \

  --resource "/subscriptions/1eb83675-114b-4f93-8921-f055b5bd6ea8/resourceGroups/cpe-autoscaling-demo-rg/providers/Microsoft.Compute/virtualMachineScaleSets/cpe-autoscaling-demo-vmss" \

Expected deployment time: 6-8 minutes  --metric "Percentage CPU" \

  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \

### Verify Deployment  --interval PT1M \

  -o table

```bash```

./check_deployment.sh

```## 🐛 Debugging



### Test Autoscaling### Ver logs en las VMs



```bash```bash

LB_IP=$(pulumi stack output load_balancer_ip)# SSH a la VM

python3 test_autoscaling.py $LB_IPssh -p 50000 azureuser@<LOAD_BALANCER_IP>

```

# Ver log de user-data

Monitor scaling in another terminal:sudo tail -f /var/log/user-data.log

```bash

watch -n 10 'az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table'# Ver log de Flask

```sudo tail -f /var/log/flask-app.log

sudo tail -f /var/log/flask-app-error.log

## Monitoring

# Ver estado del servicio Flask

### Access Dashboardssudo systemctl status flask-app.service



```bash# Ver procesos Python

LB_IP=$(pulumi stack output load_balancer_ip)ps aux | grep python

``````



- **Flask API**: http://$LB_IP/### Ver logs desde local (Azure CLI)

- **Grafana**: http://$LB_IP:3000 (admin/admin)

- **Prometheus**: http://$LB_IP:9090```bash

INSTANCE_ID=0

### Key MetricsRESOURCE_GROUP="cpe-autoscaling-demo-rg"

VMSS_NAME="cpe-autoscaling-demo-vmss"

**System Metrics (Node Exporter):**

- CPU utilization# User data log

- Memory usageaz vmss run-command invoke \

- Disk I/O  -g $RESOURCE_GROUP -n $VMSS_NAME \

- Network traffic  --instance-id $INSTANCE_ID \

  --command-id RunShellScript \

**Application Metrics (Flask Exporter):**  --scripts "tail -100 /var/log/user-data.log" \

- HTTP requests per second  --query 'value[0].message' -o tsv

- Request latency (p50, p95, p99)

- Error rates by endpoint# Flask log

- Active instancesaz vmss run-command invoke \

  -g $RESOURCE_GROUP -n $VMSS_NAME \

## Resource Cleanup  --instance-id $INSTANCE_ID \

  --command-id RunShellScript \

To destroy all infrastructure:  --scripts "tail -100 /var/log/flask-app.log" \

  --query 'value[0].message' -o tsv

```bash```

pulumi destroy

```## 🎯 Reglas de Autoscaling



## Cost Estimation| Métrica | Condición | Acción | Cooldown |

|---------|-----------|--------|----------|

Monthly cost (West US region):| CPU | > 70% por 5 min | +1 VM | 5 min |

- Standard_B1s VMSS (1-3 instances): $9-27/month| CPU | < 30% por 5 min | -1 VM | 5 min |

- Standard_B1s PostgreSQL: $12/month

- Load Balancer: $18/month**Límites**:

- NAT Gateway: $32/month + data transfer- Mínimo: 1 VM

- Public IPs: $4/month- Máximo: 3 VMs



**Total**: ~$75-95/month (with autoscaling active)## 📝 Endpoints Disponibles



## Technical Notes| Endpoint | Método | Descripción |

|----------|--------|-------------|

### Security| `/` | GET | Página principal |

| `/health` | GET | Health check |

- NSG restricts SSH access to specific IP| `/api/visit` | POST | Registrar visita |

- PostgreSQL uses password authentication| `/api/visits` | GET | Listar visitas |

- All services use systemd for process management| `/api/stress` | GET | Generar carga CPU (param: `duration`) |

- Boot diagnostics enabled for troubleshooting| `/api/metrics` | GET | Métricas del sistema |



### High Availability## 💰 Costos Estimados



- Load Balancer distributes traffic across healthy instances**Recursos (configuración económica)**:

- Health probes monitor Flask, Grafana, and Prometheus- VM Scale Set: 3x Standard_B1s (max) = ~$10/mes por VM

- Unhealthy instances are automatically removed from rotation- Load Balancer Standard: ~$18/mes

- Autoscaling replaces failed instances- Public IP Static: ~$3/mes

- PostgreSQL Flexible B1ms: ~$12/mes

### Scalability- Storage + bandwidth: ~$5/mes



- Horizontal scaling via VMSS (1-3 instances)**Total estimado**: ~$50-60/mes (con 3 VMs corriendo 24/7)

- Each instance is stateless (except for monitoring data)

- Database is centralized and shared**Optimización**: Para demo, mantener apagado cuando no se use.

- Load balancer handles connection pooling

## 🗑️ Limpieza

## Troubleshooting

```bash

### Services Not Respondingcd infrastructure-azure

pulumi destroy --yes

```bash```

# Get NAT pool port for instance (50000 + instance_id)

az network lb inbound-nat-rule list -g cpe-autoscaling-demo-rg --lb-name cpe-autoscaling-demo-lb -o table## 📚 Referencias



# SSH to instance- [Pulumi Azure Native](https://www.pulumi.com/registry/packages/azure-native/)

ssh -p 50001 azureuser@$LB_IP- [Azure VMSS Autoscaling](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-autoscale-overview)

- [PostgreSQL Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/)

# Check service status

sudo systemctl status flask-app---

sudo systemctl status prometheus

sudo systemctl status grafana-server**Autor**: Christian PE  

**Fecha**: Octubre 2025  

# View logs**IaC Tool**: Pulumi (Open Source)  

sudo journalctl -u flask-app -n 100**Cloud Provider**: Microsoft Azure

sudo tail -f /var/log/user-data.log
```

### Autoscaling Not Triggering

- Verify CPU load: Check Grafana dashboard or Azure Portal metrics
- Confirm time window: Rules require sustained CPU for 5 minutes
- Check cooldown period: 5 minutes between scaling actions
- Validate autoscale settings: `az monitor autoscale show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-autoscale`

## Author

System developed as part of Cloud Infrastructure and Autoscaling demonstration project.
