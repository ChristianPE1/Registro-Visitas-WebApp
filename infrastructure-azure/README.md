# Infraestructura Azure con Pulumi

Este directorio contiene la definición de infraestructura que despliega todo el entorno de autoscaling sobre Microsoft Azure utilizando Pulumi y el SDK de Python. Aquí encontrarás los scripts, configuraciones y guías necesarias para aprovisionar la red, balanceador, VM Scale Set, base de datos y reglas de autoscaling.

## Componentes desplegados

### Red y conectividad
- **Resource Group**: `cpe-autoscaling-demo-rg`
- **Virtual Network**: `10.0.0.0/16`
  - Subnet `10.0.1.0/24` para el VM Scale Set
  - Subnet `10.0.2.0/24` para PostgreSQL
- **Network Security Group** con reglas para HTTP (80), Flask (5000), SSH (puerto NAT), Grafana (3000) y Prometheus (9090)
- **NAT Gateway** con IP pública estática para salida a Internet

### Balanceo y cómputo
- **Public Load Balancer (Standard SKU)**
  - Health probe para Flask (`/health`)
  - NAT pool para acceso SSH (puertos 50000-50099)
  - Reglas adicionales para Grafana (3000) y Prometheus (9090)
- **Virtual Machine Scale Set**
  - Imagen base: Ubuntu 22.04 LTS
  - Tamaño: `Standard_B1s` (1 vCPU, 1 GB RAM)
  - Capacidad: mínimo 1, máximo 3 instancias
  - Custom data: clona el repositorio, instala dependencias y levanta el servicio Flask vía systemd

### Base de datos
- **PostgreSQL Flexible Server 13**
  - SKU `Standard_B1ms`
  - 32 GB de almacenamiento
  - Usuario: `autoscaling_user`
  - Contraseña configurable vía Pulumi (`db_password`)

### Autoscaling
- Métrica: `Percentage CPU`
- **Escalado horizontal (scale-out)**: CPU promedio > 70% durante 5 minutos → +1 instancia (cooldown 5 minutos)
- **Escalado hacia abajo (scale-in)**: CPU promedio < 30% durante 5 minutos → -1 instancia (cooldown 5 minutos)
- Capacidad configurada: mínimo 1, máximo 3, valor por defecto 1

## Requisitos previos

1. **Herramientas**
   - Python 3.11+
   - Pulumi CLI (`curl -fsSL https://get.pulumi.com | sh`)
   - Azure CLI (`curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`)
2. **Autenticación**
   - `az login`
   - Selecciona la suscripción correcta: `az account set --subscription <ID>`
3. **Repositorio**
   - Clonar este proyecto y ubicarse en `infrastructure-azure/`

## Configuración inicial

```bash
cd infrastructure-azure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pulumi login
pulumi stack select production-azure
```

Las contraseñas se guardan como secretos en Pulumi (`AzureAdmin2025!` y `PostgresDB2025!`). Si necesitas cambiarlas, edita directamente `__main__.py` o actualiza `pulumi config set --secret`.

## Despliegue paso a paso

```bash
# Vista previa de cambios
pulumi preview

# Aplicar la infraestructura
pulumi up --yes
```

Tiempos promedio de aprovisionamiento:
- Red y balanceador: 3-4 minutos
- PostgreSQL Flexible Server: 4-6 minutos
- VM Scale Set y extensiones: 3-4 minutos

Al finalizar, Pulumi mostrará outputs como `load_balancer_ip`, `health_endpoint`, `grafana_url`, etc.

## Scripts útiles

| Script | Descripción |
|--------|-------------|
| `check_deployment.sh` | Verifica IP pública, health check y estado del VMSS |
| `test_autoscaling.py` | Lanza carga prolongada desde Python (12 hilos, 6 minutos) |
| `monitor_instances.sh` | Muestra CPU por instancia y actualiza cada ejecución |

Ejemplo de uso:

```bash
# Verificar despliegue
./check_deployment.sh

# Ejecutar prueba de carga Python
python3 test_autoscaling.py $(pulumi stack output load_balancer_ip)
```

## Pruebas con `wrk`

`wrk` ofrece una manera sencilla y potente de generar carga:

```bash
# Instalar (Ubuntu)
sudo apt-get update && sudo apt-get install -y wrk

# Ejecutar prueba de 5 minutos con 8 hilos y 150 conexiones
LB_IP=$(pulumi stack output load_balancer_ip)
wrk -t8 -c150 -d300s --latency http://$LB_IP/
```

Mientras la prueba se ejecuta:

```bash
# Monitorear instancias
watch -n 10 'az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table'

# Ver CPU promedio del VMSS
watch -n 10 "az monitor metrics list --resource $(az vmss show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss --query id -o tsv) --metric 'Percentage CPU' --interval PT1M --query 'value[0].timeseries[0].data[-3:].{Hora:timeStamp,CPU:average}' -o table"
```

## Monitoreo detallado por instancia

Utiliza `monitor_instances.sh` para obtener la carga individual:

```bash
chmod +x monitor_instances.sh
watch -n 20 ./monitor_instances.sh
```

Cada ejecución refresca la lista de instancias, por lo que cualquier VM nueva aparecida por autoscaling será registrada en la siguiente iteración.

## Costos estimados (West US)

| Recurso | Caso 1 instancia | Caso 3 instancias |
|---------|------------------|-------------------|
| VMSS (Standard_B1s) | ~$7.59/mes | ~$22.77/mes |
| PostgreSQL Flexible Server (B1ms) | ~$12.41/mes | Idem |
| Load Balancer Standard | ~$18.26/mes | Idem |
| NAT/Public IP/Storage | ~$5/mes | ~$5/mes |
| **Total estimado** | **~$43/mes** | **~$58/mes** |

> Azure otorga $200 USD en créditos iniciales por 30 días para cuentas nuevas.

## Troubleshooting

1. **El health check falla**
   ```bash
   az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table
   ssh -p 5000X azureuser@$(pulumi stack output load_balancer_ip)
   sudo journalctl -u flask-app -n 100 --no-pager
   ```
2. **PostgreSQL no responde**
   ```bash
   az postgres flexible-server show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-postgres --query state
   ```
3. **Autoscaling no se activa**
   - Asegúrate de mantener la carga >70% durante al menos 5 minutos.
   - Verifica el historial: `az monitor autoscale show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-autoscale`

## Limpieza

```bash
pulumi destroy --yes
pulumi stack rm production-azure  # opcional
```

Esto liberará todos los recursos y evitará costos adicionales.

## Referencias

- [Documentación Pulumi para Azure](https://www.pulumi.com/registry/packages/azure-native/)
- [Azure VM Scale Sets](https://learn.microsoft.com/azure/virtual-machine-scale-sets/)
- [Azure Monitor Autoscale](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-overview)
- [PostgreSQL Flexible Server](https://learn.microsoft.com/azure/postgresql/flexible-server/)
