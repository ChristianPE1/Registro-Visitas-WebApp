# Infraestructura Azure con Pulumi

Definición de infraestructura como código usando Pulumi Python SDK para desplegar un entorno de autoscaling en Microsoft Azure.

## Recursos desplegados

### Red
- Resource Group: `cpe-autoscaling-demo-rg`
- Virtual Network: `10.0.0.0/16`
- Subnets: `10.0.1.0/24` (VMs) y `10.0.2.0/24` (PostgreSQL)
- Network Security Group con reglas para HTTP (80), Flask (5000), SSH, Grafana (3000), Prometheus (9090)
- NAT Gateway con IP pública estática

### Balanceador de carga
- Azure Load Balancer Standard SKU
- IP pública estática
- Health probe en `/health` (puerto 5000)
- Reglas de balanceo: HTTP (80→5000), Grafana (3000), Prometheus (9090)
- NAT pool para SSH (puertos 50000-50099)

### Cómputo
- Virtual Machine Scale Set (VMSS)
- Imagen: Ubuntu 22.04 LTS
- SKU: Standard_B1s (1 vCPU, 1 GB RAM)
- Capacidad: mínimo 1, máximo 5, por defecto 1
- Custom data: clona repositorio, instala dependencias, inicia Flask vía systemd

### Base de datos
- PostgreSQL Flexible Server 13
- SKU: Standard_B1ms
- Storage: 32 GB
- Usuario: `autoscaling_user`

### Autoscaling
- Métrica: Percentage CPU (promedio)
- Scale-out: CPU > 70% durante 5 minutos → +1 instancia (cooldown 5 min)
- Scale-in: CPU < 30% durante 5 minutos → -1 instancia (cooldown 5 min)

## Despliegue

```bash
cd infrastructure-azure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pulumi login
pulumi stack select production-azure
pulumi up --yes
```

Tiempo estimado: 10-15 minutos

## Pruebas de autoscaling 

### Script Python para carga extrema

Herramienta personalizada para generar carga alta en los endpoints `/api/visit` y `/api/visits`. Las bibliotecas `requests` y `concurrent.futures` se utilizan para enviar múltiples solicitudes concurrentes.

```python
python3 extreme-load.py <LB_IP>
```


## Monitoreo

```bash
# Ver instancias del VMSS
watch -n 10 ./monitor_clean.sh
```

## Endpoints de la aplicación

- `GET /health` - Health check
- `POST /api/visit` - Registrar visita (incluye procesamiento CPU intensivo)
- `GET /api/visits` - Obtener visitas (incluye cálculos hash intensivos)
- `GET /api/metrics` - Métricas de CPU y memoria
- `GET /` - Info de la API

Los endpoints `/api/visit` y `/api/visits` incluyen operaciones hash intensivas (10,000 y 50,000 iteraciones respectivamente) que consumen CPU de forma natural, simulando procesamiento real de aplicaciones.


## Limpieza

```bash
pulumi destroy --yes
```

