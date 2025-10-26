# Infraestructura Azure con Pulumi# Infrastructure as Code - Azure Implementation# Sistema de Autoscaling en Azure con Pulumi



Implementación de autoscaling horizontal en Azure usando Pulumi como herramienta IaC.



## Arquitectura Desplegada## OverviewDemo de autoscaling horizontal usando Pulumi (IaC open source) en Azure



### Componentes Principales



**Networking:**This directory contains the Infrastructure as Code (IaC) implementation using Pulumi to deploy an autoscaling web application on Microsoft Azure.## 🏗️ Arquitectura

- Virtual Network (10.0.0.0/16)

- Subnet para VMs (10.0.1.0/24)

- Subnet para PostgreSQL (10.0.2.0/24)

- Network Security Group (reglas HTTP, SSH, PostgreSQL)## Architecture- **IaC**: Pulumi Python

- Load Balancer Standard con IP pública

- NAT Pool para SSH (puertos 50000-50099)- **Cloud**: Azure (región West US)



**Compute:**### System Components- **Backend**: Flask + PostgreSQL Flexible Server (B1ms)

- VM Scale Set con Ubuntu 22.04 LTS

- Tamaño de VM: Standard_B1s (1 vCPU, 1 GB RAM)- **Frontend**: React + Tailwind CSS (local)

- Capacidad: 1-3 instancias

- Custom Script Extension para instalación automática```- **Compute**: VM Scale Set (Standard_B1s, 1-3 instancias)



**Base de Datos:**┌─────────────────────────────────────────────┐- **Load Balancer**: Azure Load Balancer con health probes

- PostgreSQL Flexible Server 13

- Tamaño: Standard_B1s│          Azure Cloud Infrastructure         │- **Database**: PostgreSQL Flexible Server 13 (Standard_B1ms, 32GB)

- Storage: 32 GB

- Integración con VNet├─────────────────────────────────────────────┤- **Autoscaling**: Basado en CPU (>70% = scale up, <30% = scale down)



**Autoscaling:**│                                             │

- Métrica: CPU porcentaje promedio

- Scale-Out: CPU > 70% por 5 minutos│  ┌───────────────────────────────────────┐ │## 📋 Requisitos

- Scale-In: CPU < 30% por 5 minutos

- Cooldown: 5 minutos│  │      Public Load Balancer             │ │



## Requisitos Previos│  │  Standard SKU with NAT Gateway        │ │- Python 3.13+



- Python 3.11 o superior│  └──────────┬────────────────────────────┘ │- Pulumi CLI

- Pulumi CLI instalado

- Azure CLI configurado (`az login`)│             │                               │- Azure CLI

- Cuenta de Azure con suscripción activa

│     ┌───────┴────────┬──────────────┐      │- Cuenta Azure con suscripción activa

## Despliegue

│     │                │              │      │

### 1. Instalar Dependencias

│  ┌──▼───┐        ┌──▼───┐      ┌──▼───┐   │## 🚀 Deployment

```bash

cd infrastructure-azure│  │ VM 1 │        │ VM 2 │      │ VM 3 │   │

python3 -m venv venv

source venv/bin/activate│  │ B1s  │        │ B1s  │      │ B1s  │   │### 1. Destruir infraestructura anterior (si existe)

pip install -r requirements.txt

```│  └──┬───┘        └──┬───┘      └──┬───┘   │



### 2. Configurar Pulumi│     │               │              │       │```bash



```bash│     └───────────────┴──────────────┘       │cd infrastructure-azure

# Login en Pulumi (elige local o cloud)

pulumi login│                     │                      │pulumi destroy --yes



# Seleccionar stack│           ┌─────────▼─────────┐            │```

pulumi stack select production-azure

```│           │ PostgreSQL Flexible│            │



### 3. Configurar Secretos│           │     Server B1s     │            │### 2. Desplegar nueva infraestructura



Las contraseñas ya están configuradas en el código:│           └────────────────────┘            │

- Admin password: `AzureAdmin2025!`

- DB password: `PostgresDB2025!`│                                             │```bash



Para cambiarlas, editar `__main__.py` directamente.└─────────────────────────────────────────────┘pulumi up --yes



### 4. Desplegar``````



```bash

# Preview de cambios

pulumi preview### Infrastructure Resources**Tiempo estimado**: 10-15 minutos



# Desplegar

pulumi up --yes

```#### Network Layer### 3. Obtener outputs



El despliegue toma aproximadamente **10-15 minutos**. Los tiempos típicos son:- **Virtual Network**: 10.0.0.0/16



- Resource Group, VNet, NSG: 1-2 min  - VM Subnet: 10.0.1.0/24```bash

- Load Balancer: 2-3 min

- PostgreSQL: 4-6 min  - Database Subnet: 10.0.2.0/24pulumi stack output

- VMSS: 3-5 min

- **Network Security Group**: Controls inbound/outbound traffic```

### 5. Verificar Despliegue

  - HTTP (80), Flask (5000), SSH (22)

```bash

# Ver outputs  - Grafana (3000), Prometheus (9090)Outputs importantes:

pulumi stack output

- **NAT Gateway**: Provides outbound internet connectivity- `load_balancer_ip`: IP pública del Load Balancer

# Obtener URL

LB_IP=$(pulumi stack output load_balancer_ip)- **Public Load Balancer**: Standard SKU- `load_balancer_url`: URL de la aplicación

echo "Aplicación: http://$LB_IP"

  - Health probes for Flask, Grafana, Prometheus- `ssh_command`: Comando para conectar por SSH

# Health check

curl http://$LB_IP/health  - Inbound NAT pool for SSH (ports 50000-50099)- `postgres_server`: FQDN del servidor PostgreSQL

```

- `health_endpoint`: Endpoint de health check

## Pruebas de Autoscaling

#### Compute Layer- `api_stress_endpoint`: Endpoint para generar carga

### Script de Carga Intensiva

- **Virtual Machine Scale Set (VMSS)**

El script `test_autoscaling.py` genera carga CPU sostenida:

  - VM Size: Standard_B1s (1 vCPU, 1 GiB RAM)## 🔧 Características Implementadas

```bash

# Obtener IP del Load Balancer  - OS: Ubuntu 22.04 LTS

LB_IP=$(pulumi stack output load_balancer_ip)

  - Capacity: 1-3 instances (autoscaling)### ✅ User Data Script Mejorado

# Ejecutar test (6 minutos de carga intensa)

python3 test_autoscaling.py $LB_IP  - Upgrade Policy: Manual

```

- **Systemd service**: Flask se ejecuta como servicio con auto-reinicio

**Configuración del test:**

- 12 threads concurrentes#### Database Layer- **Logs detallados**: `/var/log/user-data.log` y `/var/log/flask-app.log`

- Peticiones continuas de 15 segundos

- Intensidad alta (8,000,000 operaciones por petición)- **PostgreSQL Flexible Server**- **Health checks**: Verifica que Flask esté corriendo antes de completar

- Duración total: 6 minutos

  - SKU: Standard_B1s (1 vCore, 2 GiB RAM, 32 GB storage)- **Frontend**: Instala dependencias de React (opcional)

### Monitoreo del Autoscaling

  - Version: 13- **Manejo de errores**: Script con `set -ex` para debugging

En una terminal separada, ejecutar:

  - Firewall: Azure services allowed

```bash

watch -n 10 'az vmss list-instances \### ✅ SSH Access vía NAT Pool

  -g cpe-autoscaling-demo-rg \

  -n cpe-autoscaling-demo-vmss \#### Monitoring Layer

  -o table'

```Each VM instance includes:Las VMs son accesibles por SSH a través del Load Balancer:



### Timeline Esperado- **Prometheus**: Metrics collection and storage (port 9090)



Basado en la configuración de autoscaling:- **Grafana**: Metrics visualization (port 3000)```bash



**Minuto 0-1:** Sistema estable (1 instancia, CPU ~20%)- **Node Exporter**: System metrics (port 9100)# VM 0 (primera instancia)



**Minuto 1-5:** Carga aplicada (1 instancia, CPU >70% sostenida)- **Flask Prometheus Exporter**: Application metricsssh -p 50000 azureuser@<LOAD_BALANCER_IP>



**Minuto 5-6:** Azure detecta umbral, inicia scale-out



**Minuto 6-8:** Nueva instancia provisionándose### Application Stack# VM 1 (segunda instancia, si existe)



**Minuto 8-10:** 2 instancias activas, carga distribuida (CPU ~40%)ssh -p 50001 azureuser@<LOAD_BALANCER_IP>



**Minuto 10-15:** Carga termina, CPU baja <30%Each VMSS instance runs:



**Minuto 15-20:** Azure detecta umbral, inicia scale-in1. **Flask Backend** (Python 3, port 5000)# VM 2 (tercera instancia, si existe)



**Minuto 20-22:** Retorno a 1 instancia   - REST API for visits managementssh -p 50002 azureuser@<LOAD_BALANCER_IP>



## Verificación del Despliegue   - PostgreSQL connection with fallback```



### Script Automático   - Prometheus metrics export



```bash2. **Monitoring Services****Password**: `AzureAdmin2025!`

./check_deployment.sh

```   - Prometheus server



Este script verifica:   - Grafana dashboard### ✅ Boot Diagnostics Habilitado

- Load Balancer responde

- Endpoint `/health` está operativo   - Node exporter for system metrics

- Estado del VMSS

- Conexión a PostgreSQLLos boot diagnostics están activos en el VMSS:



### Verificación Manual### Autoscaling Configuration



```bash- Acceso a Serial Console en Azure Portal

# 1. Ver recursos desplegados

az resource list -g cpe-autoscaling-demo-rg -o table**Scale-Out Rule:**- Logs de arranque disponibles



# 2. Ver instancias del VMSS- Trigger: Average CPU > 70%- Troubleshooting mejorado

az vmss list-instances \

  -g cpe-autoscaling-demo-rg \- Time Window: 5 minutes

  -n cpe-autoscaling-demo-vmss \

  -o table- Action: Add 1 VM instance## 🧪 Testing



# 3. Ver estado de PostgreSQL- Cooldown: 5 minutes

az postgres flexible-server show \

  -g cpe-autoscaling-demo-rg \### Health Check

  -n cpe-autoscaling-demo-postgres \

  --query state**Scale-In Rule:**



# 4. Ver reglas de autoscaling- Trigger: Average CPU < 30%```bash

az monitor autoscale show \

  -g cpe-autoscaling-demo-rg \- Time Window: 5 minutescurl http://<LOAD_BALANCER_IP>/health

  -n cpe-autoscaling-demo-vmss-autoscale

```- Action: Remove 1 VM instance```



### Conectar por SSH- Cooldown: 5 minutes



```bashRespuesta esperada:

# Obtener puerto NAT de la primera instancia

az vmss list-instance-connection-info \**Limits:**```json

  -g cpe-autoscaling-demo-rg \

  -n cpe-autoscaling-demo-vmss- Minimum: 1 instance{



# Conectar (puerto 50000 para instancia 0, 50001 para instancia 1, etc.)- Maximum: 3 instances  "status": "healthy",

ssh azureuser@$(pulumi stack output load_balancer_ip) -p 50000

```- Default: 1 instance  "database": "connected",



## Endpoints de la API  "timestamp": "2025-10-25T..."



| Endpoint | Método | Descripción |## Service Communication}

|----------|--------|-------------|

| `/health` | GET | Health check (incluye estado de BD) |```

| `/api/visit` | POST | Registrar una visita |

| `/api/visits` | GET | Obtener contador de visitas |### Load Balancer Rules

| `/api/stress` | GET | Simular carga CPU |

| `/api/metrics` | GET | Métricas de CPU/memoria |### Stress Test Automatizado

| `/` | GET | Información de la API |

| Frontend Port | Backend Port | Service | Protocol |

### Ejemplo: Endpoint de Estrés

|--------------|--------------|---------|----------|```bash

```bash

# Carga ligera (10 segundos)| 80 | 5000 | Flask API | TCP |python3 test_autoscaling.py <LOAD_BALANCER_IP>

curl "http://$LB_IP/api/stress?duration=10&intensity=5000000"

| 3000 | 3000 | Grafana | TCP |```

# Carga intensa (60 segundos)

curl "http://$LB_IP/api/stress?duration=60&intensity=8000000"| 9090 | 9090 | Prometheus | TCP |

```

| 50000-50099 | 22 | SSH (NAT Pool) | TCP |Este script:

## Gestión de Recursos

1. Verifica el health endpoint

### Detener sin Destruir

### Data Flow2. Obtiene métricas iniciales

```bash

# Escalar a 0 instancias3. Genera carga CPU con 5 threads concurrentes (60s cada uno)

az vmss scale \

  --resource-group cpe-autoscaling-demo-rg \1. **Inbound Traffic**: Client → Load Balancer → VMSS instances (round-robin)4. Muestra métricas finales

  --name cpe-autoscaling-demo-vmss \

  --new-capacity 02. **Database Access**: VMSS instances → PostgreSQL Flexible Server (private connection)5. Proporciona instrucciones de monitoreo



# Detener PostgreSQL3. **Outbound Traffic**: VMSS instances → NAT Gateway → Internet

az postgres flexible-server stop \

  --resource-group cpe-autoscaling-demo-rg \4. **Monitoring**: Prometheus (per instance) → Collects from Flask + Node Exporter### Debug Helper Interactivo

  --name cpe-autoscaling-demo-postgres

```5. **Visualization**: Grafana → Queries local Prometheus



### Reactivar```bash



```bash## Files./debug_helper.sh

# Iniciar PostgreSQL

az postgres flexible-server start \```

  --resource-group cpe-autoscaling-demo-rg \

  --name cpe-autoscaling-demo-postgres- `__main__.py`: Main Pulumi infrastructure definition



# Escalar a 1 instancia- `Pulumi.yaml`: Project configurationMenú interactivo con opciones para:

az vmss scale \

  --resource-group cpe-autoscaling-demo-rg \- `Pulumi.production-azure.yaml`: Stack-specific settings1. SSH a cualquier VM

  --name cpe-autoscaling-demo-vmss \

  --new-capacity 1- `requirements.txt`: Python dependencies for Pulumi2. Verificar health endpoint

```

- `test_autoscaling.py`: Load test script for autoscaling validation3. Ver instancias del VMSS

### Destruir Infraestructura

- `check_deployment.sh`: Deployment verification script4. Ver métricas de CPU

```bash

cd infrastructure-azure5. Ejecutar stress test

pulumi destroy --yes

```## Deployment6. Ver logs via Azure CLI



## Costos Estimados



Costos mensuales aproximados (región West US):### Prerequisites## 📊 Monitoreo de Autoscaling



| Recurso | Especificación | Costo Mensual |

|---------|---------------|---------------|

| VMSS | 1x Standard_B1s | $7.59 |- Azure CLI installed and authenticated### Vía Azure Portal

| VMSS | 3x Standard_B1s (máximo) | $22.77 |

| PostgreSQL | Standard_B1s | $12.41 |- Pulumi CLI installed

| Load Balancer | Standard SKU | $18.26 |

| IP Pública | Estática | $3.65 |- Python 3.8+1. Ir a: **Virtual Machine Scale Sets** > `cpe-autoscaling-demo-vmss`

| Storage | 32 GB Standard LRS | $1.54 |

| **Total (1 instancia)** | | **$43.45/mes** |2. Click en **Instances** para ver número de VMs

| **Total (3 instancias)** | | **$58.63/mes** |

### Configuration3. Click en **Metrics** para ver CPU percentage

> Nota: Azure ofrece $200 en créditos gratuitos durante 30 días para cuentas nuevas.

4. Click en **Autoscale** para ver reglas activas

## Troubleshooting

Set required secrets:

### Error: No se puede conectar a la aplicación

```bash### Vía Azure CLI

```bash

# Verificar estado de las VMspulumi config set --secret admin_password <PASSWORD>

az vmss list-instances \

  -g cpe-autoscaling-demo-rg \pulumi config set --secret db_password <PASSWORD>```bash

  -n cpe-autoscaling-demo-vmss \

  -o tablepulumi config set location westus# Ver instancias



# Ver logs de una VM```az vmss list-instances \

az vmss get-instance-view \

  -g cpe-autoscaling-demo-rg \  -g cpe-autoscaling-demo-rg \

  -n cpe-autoscaling-demo-vmss \

  --instance-id 0### Deploy Infrastructure  -n cpe-autoscaling-demo-vmss \

```

  --query '[].{Name:name, State:provisioningState, InstanceID:instanceId}' \

### Error: PostgreSQL no conecta

```bash  -o table

```bash

# Verificar estadocd infrastructure-azure

az postgres flexible-server show \

  -g cpe-autoscaling-demo-rg \pulumi up# Ver métricas CPU (últimos 30 min)

  -n cpe-autoscaling-demo-postgres

```az monitor metrics list \

# Ver reglas de firewall

az postgres flexible-server firewall-rule list \  --resource "/subscriptions/1eb83675-114b-4f93-8921-f055b5bd6ea8/resourceGroups/cpe-autoscaling-demo-rg/providers/Microsoft.Compute/virtualMachineScaleSets/cpe-autoscaling-demo-vmss" \

  -g cpe-autoscaling-demo-rg \

  -n cpe-autoscaling-demo-postgresExpected deployment time: 6-8 minutes  --metric "Percentage CPU" \

```

  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \

### El autoscaling no se activa

### Verify Deployment  --interval PT1M \

Verificar:

1. La carga debe sostenerse por 5 minutos continuos  -o table

2. CPU debe estar >70% (promedio entre todas las instancias)

3. Cooldown de 5 minutos entre operaciones```bash```

4. Máximo de 3 instancias configurado

./check_deployment.sh

```bash

# Ver historial de autoscaling```## 🐛 Debugging

az monitor autoscale show \

  -g cpe-autoscaling-demo-rg \

  -n cpe-autoscaling-demo-vmss-autoscale

### Test Autoscaling### Ver logs en las VMs

# Ver métricas de CPU

az monitor metrics list \

  --resource $(az vmss show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss --query id -o tsv) \

  --metric "Percentage CPU" \```bash```bash

  --start-time $(date -u -d '30 minutes ago' '+%Y-%m-%dT%H:%M:%SZ')

```LB_IP=$(pulumi stack output load_balancer_ip)# SSH a la VM



## Arquitectura del Códigopython3 test_autoscaling.py $LB_IPssh -p 50000 azureuser@<LOAD_BALANCER_IP>



### Archivos Principales```



- `__main__.py`: Definición completa de infraestructura Pulumi# Ver log de user-data

- `Pulumi.yaml`: Configuración del proyecto

- `Pulumi.production-azure.yaml`: Configuración del stackMonitor scaling in another terminal:sudo tail -f /var/log/user-data.log

- `requirements.txt`: Dependencias Python de Pulumi

- `test_autoscaling.py`: Script de prueba de carga```bash

- `check_deployment.sh`: Script de verificación

watch -n 10 'az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table'# Ver log de Flask

### Modificar Configuración

```sudo tail -f /var/log/flask-app.log

Para cambiar parámetros de autoscaling, editar en `__main__.py`:

sudo tail -f /var/log/flask-app-error.log

```python

# Líneas 440-492: AutoscaleSettings## Monitoring

autoscale_setting = autoscale.AutoscaleSetting(

    resource_name_=f"{project_name}-vmss-autoscale",# Ver estado del servicio Flask

    ...

    profiles=[### Access Dashboardssudo systemctl status flask-app.service

        autoscale.AutoscaleProfileArgs(

            capacity=autoscale.ScaleCapacityArgs(

                minimum="1",    # Cambiar aquí

                maximum="3",    # Cambiar aquí```bash# Ver procesos Python

                default="1"     # Cambiar aquí

            ),LB_IP=$(pulumi stack output load_balancer_ip)ps aux | grep python

            rules=[

                # Scale-out rule``````

                autoscale.ScaleRuleArgs(

                    metric_trigger=autoscale.MetricTriggerArgs(

                        threshold=70.0,  # Cambiar umbral aquí

                        time_window="PT5M"  # Ventana de tiempo- **Flask API**: http://$LB_IP/### Ver logs desde local (Azure CLI)

                    ),

                    ...- **Grafana**: http://$LB_IP:3000 (admin/admin)

                ),

                # Scale-in rule- **Prometheus**: http://$LB_IP:9090```bash

                autoscale.ScaleRuleArgs(

                    metric_trigger=autoscale.MetricTriggerArgs(INSTANCE_ID=0

                        threshold=30.0,  # Cambiar umbral aquí

                        time_window="PT5M"### Key MetricsRESOURCE_GROUP="cpe-autoscaling-demo-rg"

                    ),

                    ...VMSS_NAME="cpe-autoscaling-demo-vmss"

                )

            ]**System Metrics (Node Exporter):**

        )

    ]- CPU utilization# User data log

)

```- Memory usageaz vmss run-command invoke \



## Recursos Adicionales- Disk I/O  -g $RESOURCE_GROUP -n $VMSS_NAME \



- [Pulumi Azure Documentation](https://www.pulumi.com/docs/clouds/azure/)- Network traffic  --instance-id $INSTANCE_ID \

- [Azure VMSS Documentation](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/)

- [Azure Autoscale Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/autoscale/)  --command-id RunShellScript \

- [PostgreSQL Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/)

**Application Metrics (Flask Exporter):**  --scripts "tail -100 /var/log/user-data.log" \

## Licencia

- HTTP requests per second  --query 'value[0].message' -o tsv

MIT License

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
